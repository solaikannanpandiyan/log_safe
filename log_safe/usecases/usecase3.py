import logging
import time
from log_safe import initialize_safe_logging
import multiprocessing

## 3. Long-Running Process with Progress Logging
initialize_safe_logging()

def long_running_task(duration):
    logger = logging.getLogger()
    start_time = time.time()
    while time.time() - start_time < duration:
        elapsed = time.time() - start_time
        progress = (elapsed / duration) * 100
        logger.info(f"Task progress: {progress:.2f}%")
        time.sleep(1)
    logger.info("Task completed")

if __name__ == "__main__":
    logger = logging.getLogger()
    logger.info("Starting long-running task")

    process = multiprocessing.Process(target=long_running_task, args=(5,))
    process.start()

    logger.info("Main process waiting for task to complete")
    process.join()

    logger.info("All tasks completed")