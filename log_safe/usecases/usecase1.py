import logging
from log_safe import initialize_safe_logging
import multiprocessing

## 1. Basic Multiprocessing with Logging
initialize_safe_logging()

def worker_function(x):
    logger = logging.getLogger()
    logger.info(f"Processing item {x}")
    return x * 2

if __name__ == "__main__":
    logger = logging.getLogger()
    logger.info("Starting multiprocessing task")

    with multiprocessing.Pool(processes=4) as pool:
        results = pool.map(worker_function, range(10))

    logger.info(f"Processing complete. Results: {results}")