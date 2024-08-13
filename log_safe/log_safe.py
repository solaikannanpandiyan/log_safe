import functools
import logging
import logging.config
import multiprocessing
import queue
import atexit
import sys
import threading
import time
from logging.handlers import QueueHandler
from concurrent.futures import ProcessPoolExecutor

from log_safe.config import DEFAULT_LISTENER_CONFIG, DEFAULT_WORKER_CONFIG

"""
Global variables used throughout the module:
- _global_log_queue: Stores the queue used for inter-process logging communication
- _worker_log_config: Stores the logging configuration for worker processes
- isInitialized: Flag to ensure the logging system is initialized only once
- target_function: Placeholder for the original target function in processes
"""
_global_log_queue = None
_worker_log_config = None
isInitialized = False
target_function = None


def set_global_log_queue(queue):
    global _global_log_queue
    _global_log_queue = queue


def set_worker_log_config(config):
    global _worker_log_config
    _worker_log_config = config


class ListenerProcess:
    """
    ListenerProcess class:
    Handles the central logging process that receives log records from all worker processes.
    It configures logging, processes incoming log records, and includes a watchdog
    to shut down if idle for too long.
    """

    def __init__(self, input_queue, log_config):
        self.queue = input_queue
        self.log_config = log_config
        self.shutdown_flag = threading.Event()
        self.last_log_time = time.time()
        self.configure_logging()
        self.start_watchdog()

    def configure_logging(self):
        logging.config.dictConfig(self.log_config)

    def run(self):
        """
        Main loop of the listener process:
        - Retrieves log records from the queue
        - Processes each record using the appropriate logger
        - Handles exceptions and continues processing
        """
        while not self.shutdown_flag.is_set():
            try:
                record = self.queue.get(timeout=1)
                if record is None:
                    break
                logger = logging.getLogger(record.name)
                logger.handle(record)
                self.last_log_time = time.time()
            except queue.Empty:
                continue
            except Exception:
                import traceback
                print('Error in listener process:', file=sys.stderr)
                traceback.print_exc(file=sys.stderr)

    def stop(self):
        self.shutdown_flag.set()
        self.queue.put_nowait(None)

    def _watchdog(self):
        """
        Watchdog thread:
        Monitors the listener process and shuts it down if it's been idle for too long.
        This prevents resource waste in case of unexpected issues.
        """
        idle_timeout = self.log_config.get('idle_timeout', 600 * 60)
        while not self.shutdown_flag.is_set():
            time.sleep(60)
            if time.time() - self.last_log_time > idle_timeout:
                print("Logging system idle for too long. Shutting down.")
                self.stop()
                break

    def start_watchdog(self):
        watchdog_thread = threading.Thread(target=self._watchdog, daemon=True)
        watchdog_thread.start()


class SafeLogger:
    """
    SafeLogger class:
    Manages the overall logging setup, including:
    - Creating and managing the central logging queue
    - Starting and stopping the listener process
    - Providing a configured logger for worker processes
    """

    def __init__(self, listener_config, worker_config):
        self.log_queue = multiprocessing.Manager().Queue(-1)
        self.listener_process = None
        self.listener_config = listener_config
        self.worker_config = worker_config

    def start_listener(self):
        self.listener_process = original_process(
            target=self._run_listener,
            args=(self.log_queue, self.listener_config),
            daemon=True
        )
        self.listener_process.start()
        atexit.register(self.stop_listener)

    @staticmethod
    def _run_listener(queue, log_config):
        listener = ListenerProcess(queue, log_config)
        listener.run()

    def stop_listener(self):
        self.log_queue.put_nowait(None)
        self.listener_process.join()

    def get_logger(self):
        logging.config.dictConfig(self.worker_config)
        rootlogger = logging.getLogger("root")
        queue_handler = QueueHandler(self.log_queue)
        rootlogger.addHandler(queue_handler)
        return rootlogger


def worker_process_initializer(global_log_queue, global_worker_config):
    """
    Initializes logging for a worker process:
    - Sets up the global log queue and worker config
    - Configures logging based on the provided configuration
    - Adds a QueueHandler to the root logger to send logs to the central process
    """
    if not global_log_queue:
        raise ValueError("Global log queue is not set or perhaps you are performing nested process creation")

    set_worker_log_config(global_worker_config)
    set_global_log_queue(global_log_queue)

    logging.config.dictConfig(global_worker_config)

    root_logger = logging.getLogger("root")
    queue_handler = QueueHandler(global_log_queue)
    root_logger.addHandler(queue_handler)


def initialize_safe_logging(listener_config=None, worker_config=None):
    """
    Main function to initialize the safe logging system:
    - Ensures initialization happens only once in the main process
    - Sets up the SafeLogger with provided or default configurations
    - Starts the listener process and sets up global variables
    """
    global isInitialized
    if multiprocessing.current_process().name == 'MainProcess' and not isInitialized:
        isInitialized = True
        if listener_config is None:
            listener_config = DEFAULT_LISTENER_CONFIG

        if worker_config is None:
            worker_config = DEFAULT_WORKER_CONFIG

        safe_logger = SafeLogger(listener_config, worker_config)
        safe_logger.start_listener()

        set_global_log_queue(safe_logger.log_queue)
        set_worker_log_config(worker_config)

        safe_logger.get_logger()


def combined_initializer(*args):
    """
    Helper function for ensuring proper initialization in child processes:
    - Extracts necessary arguments for worker process initialization
    - Initializes the worker process logging
    - Calls the original target function if provided

    This function is crucial for maintaining logging consistency across all processes.
    """
    worker_process_initializer = None
    queue = None
    config = None
    original_target = None
    original_args = None

    if args and callable(args[-1]):
        try:
            worker_process_initializer = args[-1]
            config = args[-2]
            queue = args[-3]
        except Exception as ex:
            print("one among worker_process_initializer or queue or config is missing or none")
            raise ex

    worker_process_initializer(queue, config)

    args = args[:-3]

    if args and callable(args[-1]):
        try:
            original_target = args[-1]
            original_args = args[:-1]
        except Exception as ex:
            print("one among original_target or original_args is missing or none")
            raise ex

    if not original_target:
        return

    if not original_args:
        original_target()
    else:
        original_target(*original_args)


_original_init = ProcessPoolExecutor.__init__


def _patched_process_executor_init(self, *args, **kwargs):
    """
    Patched initialization for ProcessPoolExecutor:
    - Injects the combined_initializer into the executor's initialization
    - Ensures that all processes created by the executor use safe logging
    """
    global _global_log_queue, _worker_log_config

    if 'initializer' in kwargs:
        original_initializer = kwargs['initializer']
        kwargs['initializer'] = combined_initializer
        if 'initargs' in kwargs:
            kwargs['initargs'] = tuple(
                list(kwargs['initargs']) + [original_initializer, _global_log_queue, _worker_log_config,
                                            worker_process_initializer])
        else:
            kwargs['initargs'] = (
            original_initializer, _global_log_queue, _worker_log_config, worker_process_initializer)
    else:
        kwargs['initargs'] = (_global_log_queue, _worker_log_config, worker_process_initializer)
        kwargs['initializer'] = combined_initializer

    _original_init(self, *args, **kwargs)


ProcessPoolExecutor.__init__ = _patched_process_executor_init

original_pool = multiprocessing.Pool


def safe_logging_pool(*args, **kwargs):
    """
    Custom Pool function with safe logging:
    - Injects the combined_initializer into the Pool's initialization
    - Ensures that all processes created by the Pool use safe logging
    """
    global _global_log_queue, _worker_log_config

    if 'initializer' in kwargs:
        original_initializer = kwargs['initializer']
        kwargs['initializer'] = combined_initializer
        if 'initargs' in kwargs:
            kwargs['initargs'] = tuple(
                list(kwargs['initargs']) + [original_initializer, _global_log_queue, _worker_log_config,
                                            worker_process_initializer])
        else:
            kwargs['initargs'] = (
                original_initializer, _global_log_queue, _worker_log_config, worker_process_initializer)
    else:
        kwargs['initargs'] = (_global_log_queue, _worker_log_config, worker_process_initializer)
        kwargs['initializer'] = combined_initializer

    return original_pool(*args, **kwargs)


multiprocessing.Pool = safe_logging_pool

original_process = multiprocessing.Process


class SafeProcess(original_process):
    """
    SafeProcess class:
    A patched version of multiprocessing.Process that ensures safe logging:
    - Wraps the original target function with the combined_initializer
    - Injects necessary logging setup arguments
    """

    def __init__(self, *args, **kwargs):
        global _global_log_queue, _worker_log_config
        if 'target' in kwargs:
            original_target = kwargs['target']
            kwargs['target'] = combined_initializer
            if 'args' in kwargs:
                kwargs['args'] = tuple(list(kwargs['args']) + [original_target, _global_log_queue, _worker_log_config,
                                                               worker_process_initializer])
            else:
                kwargs['args'] = (original_target, _global_log_queue, _worker_log_config, worker_process_initializer)

        super().__init__(*args, **kwargs)


multiprocessing.Process = SafeProcess