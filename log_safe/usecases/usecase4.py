import logging
from log_safe import initialize_safe_logging
import multiprocessing

## 4. Error Handling and Logging in Multiple Processes
initialize_safe_logging()

def error_prone_function(x):
    logger = logging.getLogger()
    try:
        if x == 5:
            raise ValueError("Error processing item 5")
        result = 10 / x
        logger.info(f"Processed item {x}, result: {result}")
        return result
    except Exception as e:
        logger.error(f"Error processing item {x}: {str(e)}")
        return None

if __name__ == "__main__":
    logger = logging.getLogger()
    logger.info("Starting error-prone tasks")

    with multiprocessing.Pool(processes=4) as pool:
        results = pool.map(error_prone_function, range(10))

    logger.info(f"All tasks completed. Results: {results}")