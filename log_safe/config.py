
DEFAULT_LISTENER_CONFIG = {
                'version': 1,
                'disable_existing_loggers': False,
                'formatters': {
                    'standard': {
                        'format': '%(asctime)s - %(processName)s - %(threadName)s - %(levelname)s - %(message)s'
                    },
                },
                'handlers': {
                    'file': {
                        'class': 'logging.handlers.RotatingFileHandler',
                        'filename': 'app.log',
                        'maxBytes': 10 * 1024 * 1024, # bytes
                        'backupCount': 1, # no of files
                        'formatter': 'standard',
                    },
                },
                'root': {
                    'handlers': ['file'],
                    'level': 'DEBUG',
                },
                'idle_timeout': 600 * 60
            }

DEFAULT_WORKER_CONFIG = {
                'version': 1,
                'disable_existing_loggers': False,
                'formatters': {
                    'standard': {
                        'format': '%(asctime)s - %(processName)s - %(threadName)s - %(levelname)s - %(name)s - %(message)s'
                    },
                },
                'handlers': {
                    'console': {
                        'class': 'logging.StreamHandler',
                        'formatter': 'standard',
                    },
                },
                'root': {
                    'handlers': ['console'],
                    'level': 'DEBUG',
                },
            }