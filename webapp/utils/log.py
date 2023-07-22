import logging
import inspect
import datetime



class MyAppLogger(logging.Logger):
    def __init__(self, name, level=logging.NOTSET, timestamp=False):
        super().__init__(name, level)

        self.timestamp = timestamp
        # Create a formatter
        formatter = logging.Formatter("%(levelname)s: %(message)s")
        # formatter = logging.Formatter(f"{'%(asctime)s:' if timestamp else ''}%(levelname)s: %(message)s")
        # formatter = logging.Formatter('%(message)s')

        # Create file handler (optional)
        self.file_handler = logging.FileHandler('app.log')
        self.file_handler.setLevel(logging.DEBUG)  # Set the log level for the file handler
        self.file_handler.setFormatter(formatter)
        # self.addHandler(self.file_handler)

        # Create console handler
        self.console_handler = logging.StreamHandler()
        self.console_handler.setLevel(read_level())  # Set the log level for the console handler
        self.console_handler.setFormatter(formatter)
        self.addHandler(self.console_handler)
        # self.dbg_lvl = read_level()


        custom_handler = logging.StreamHandler()
        custom_handler.setLevel(logging.WARNING)
        self.addHandler(custom_handler)

    def enable_file_logging(self):
        """Enable file logging."""
        self.addHandler(self.file_handler)

    def disable_file_logging(self):
        """Disable file logging."""
        self.removeHandler(self.file_handler)

    def enable_console_logging(self):
        """Enable console logging."""
        self.addHandler(self.console_handler)

    def disable_console_logging(self):
        """Disable console logging."""
        self.removeHandler(self.console_handler)

    def set_log_level(self, level):
        """
        Set the log level for the logger.

        Args:
            level (str): Log level (e.g., 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL').
        """
        self.setLevel(level.upper())
        self.file_handler.setLevel(level.upper())
        self.console_handler.setLevel(level.upper())

    def log_with_metadata(self, level, message, depth = 0, timestamp=False):
        """
        Log a message with metadata such as function name and line number.

        Args:
            level (str): Log level (e.g., 'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL').
            message (str): Log message.
            timestamp (bool, optional): Include timestamp in the log message. Default is False.
        """
        frame = inspect.currentframe().f_back
        for i in range(0, depth):
            frame = frame.f_back
        file_name = frame.f_code.co_filename
        func_name = frame.f_code.co_name
        line_number = frame.f_lineno


        if timestamp or self.timestamp:
            message = f'{self.get_timestamp()} - {message}'

        log_message = f'File \"{file_name}\", line {line_number}, in {func_name}\n{message}\n'
        self.log(level, log_message)

    def error(self, message, timestamp=False):
        self.log_with_metadata(logging.ERROR, message, timestamp)

    def debug(self, message, timestamp=False):
        self.log_with_metadata(logging.DEBUG, message, timestamp)

    def info(self, message, timestamp=False):
        self.log(logging.INFO, message)

    def defualt(self, message):
        self.log_with_metadata(self.level, message)

    

    @staticmethod
    def get_timestamp():
        """Get the current timestamp in a specific format."""
        return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    def read_level(self):
        level = logging.INFO  # Default level if 'instance/dbg' does not exist

        try:
            with open('instance/dbg', 'r') as f:
                level_str = f.readline().strip()
                if level_str.isdigit():
                    level = int(level_str)
                else:
                    level = getattr(logging, level_str.upper(), level)
                
                tstamp = f.readline().strip().lower()
                if tstamp in {"1", "on", "yes", "y", "true"}:
                    self.timestamp = True
        except FileNotFoundError:
            pass

        return level

class CustomLoggerWrapper:
    def __init__(self, name):
        self.logger = logging.getLogger(name)
        self.formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(pathname)s - %(lineno)d - %(message)s')

    def add_handler(self, handler):
        handler.setFormatter(self.formatter)
        self.logger.addHandler(handler)

    def info(self, message):
        self.logger.info(message, stack_info=True)

    def warning(self, message):
        self.logger.warning(message, stack_info=True)

    def error(self, message):
        self.logger.error(message, stack_info=True)

    def exception(self, message):
        self.logger.exception(message)

    def critical(self, message):
        self.logger.critical(message, stack_info=True)


# # Example usage in a Flask app

# from flask import Flask
# app = Flask(__name__)

# # Instantiate the logger
# logger = MyAppLogger('my_app_logger', level=logging.DEBUG)

# # Enable file logging
# logger.enable_file_logging()

# # Disable console logging
# logger.disable_console_logging()

# # Set log level
# logger.set_log_level('DEBUG')

# # Usage examples
# @app.route('/')
# def home():
#     logger.log_with_metadata('debug', 'This is a debug message', timestamp=True)
#     logger.log_with_metadata('info', 'This is an info message', timestamp=True)
#     logger.log_with_metadata('warning', 'This is a warning message', timestamp=True)
#     logger.log_with_metadata('error', 'This is an error message', timestamp=True)
#     logger.log_with_metadata('critical', 'This is a critical message', timestamp=True)

#     return 'Hello, World!'

# if __name__ == '__main__':
#     app.run()
