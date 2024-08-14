# log_safe

`log_safe` is a Python library that provides safe and efficient logging capabilities for multiprocessing applications. It ensures that logging is thread-safe and process-safe, making it ideal for complex, multi-process Python applications.

## Features

- Thread-safe and process-safe logging
- Centralized log collection from multiple processes
- Customizable logging configurations for both listener and worker processes
- Automatic initialization of logging in child processes
- Watchdog mechanism to prevent hanging listener process daemons
- Seamless integration with Python's built-in `multiprocessing` and `concurrent.futures` modules

## Quick Start

Here's a simple example of how to use `log_safe`:

```python
from log_safe import initialize_safe_logging
import logging
import multiprocessing

initialize_safe_logging()

def worker_function():
    logger = logging.getLogger()
    logger.info("This is a log message from a worker process")

if __name__ == "__main__":
    logger = logging.getLogger()

    logger.info("Starting main process")

    with multiprocessing.Pool(processes=2) as pool:
        pool.apply_async(worker_function)
        pool.apply_async(worker_function)

    logger.info("Main process completed")
```

## Usage

1. Initialize logging before using any multiprocessing features:

```python
from log_safe import initialize_safe_logging

initialize_safe_logging()
```

2. Use with `multiprocessing.Pool`, `ProcessPoolExecutor`, or `multiprocessing.Process` as you normally would. `log_safe` automatically patches these to ensure proper logging initialization in all child processes.

## Custom Configuration

You can provide custom configurations for both the listener and worker processes:

```python
from log_safe import initialize_safe_logging

listener_config = {
    # ... listener configuration ...
}

worker_config = {
    # ... worker configuration ...
}

initialize_safe_logging(listener_config, worker_config)
```

## Considerations

- Always call `initialize_safe_logging()` in the main process before creating any child processes.
- The library uses global variables to maintain the logging state. Be cautious when modifying global state in your application.
- The watchdog mechanism will shut down the logging system if it's idle for too long (default is 10 hours). Adjust this if needed for long-running applications.

For more detailed information, use cases, and advanced usage, please refer to the full documentation on [GitHub](https://github.com/solaikannanpandiyan/log_safe).