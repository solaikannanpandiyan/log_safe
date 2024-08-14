import logging
from log_safe import initialize_safe_logging
from concurrent.futures import ProcessPoolExecutor
import math

## 2. Using ProcessPoolExecutor with Custom Logging Configuration

custom_config = {
    'version': 1,
    'formatters': {
        'detailed': {
            'format': '%(asctime)s - %(processName)s - %(name)s - %(levelname)s - %(message)s'
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'detailed',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'calculations.log',
            'formatter': 'detailed',
        },
    },
    'root': {
        'level': 'INFO',
    },
    'loggers': {
        'complex_calculation': {
            'level': 'INFO',
            'handlers': ['file'],
        },
    }
    }

initialize_safe_logging(worker_config=custom_config)

def complex_calculation(x):
    logger = logging.getLogger('complex_calculation')
    result = math.factorial(x)
    logger.info(f"Factorial of {x} is {result}")
    return result

if __name__ == "__main__":
    logger = logging.getLogger()
    logger.info("Starting complex calculations")

    with ProcessPoolExecutor(max_workers=4) as executor:
        results = list(executor.map(complex_calculation, range(10)))

    logger.info(f"Calculations complete. Results: {results}")