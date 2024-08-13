import logging
import threading
from log_safe import initialize_safe_logging
import multiprocessing
import time

## 5. Combining Threading and Multiprocessing with Logging
initialize_safe_logging()


def thread_function(name):
    logger = logging.getLogger(__name__)
    logger.info(f"Thread {name} starting")
    time.sleep(2)
    logger.info(f"Thread {name} finishing")


def process_function(process_name):
    logger = logging.getLogger(__name__)
    logger.info(f"Process {process_name} starting")

    threads = []
    for i in range(3):
        t = threading.Thread(target=thread_function, args=(f"{process_name}-Thread-{i}",))
        threads.append(t)
        t.start()

    for t in threads:
        t.join()

    logger.info(f"Process {process_name} finishing")


if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    logger.info("Starting combined threading and multiprocessing task")

    processes = []
    for i in range(3):
        p = multiprocessing.Process(target=process_function, args=(f"Process-{i}",))
        processes.append(p)
        p.start()

    for p in processes:
        p.join()

    logger.info("All tasks completed")