# pip install python-json-logger for structured logging in json

# A handler decides where the log output goes — to the console (stdout), to a file, 
# to a remote service. Think of it as the destination.

# A formatter decides what the log output looks like — plain text, JSON, how the timestamp 
# is formatted, which fields are included. Think of it as the shape of the message.

# The relationship is: the formatter rides on top of the handler. You create a formatter, 
# attach it to a handler, then attach the handler to the logger. The logger generates the event, 
# the formatter shapes it, the handler sends it to the destination.

import logging
from pythonjsonlogger import jsonlogger

# This function configures the root logger with a JSON formatter and stdout handler so all 
# application logs are structured and readable by CloudWatch and Sentry.

# Setup logging function
def setup_logging(level=logging.INFO):
    # Create a logger
    logger = logging.getLogger()
    # Set the level
    logger.setLevel(level)
    # Create a handler
    logHandler = logging.StreamHandler()
    # Create a Json formatter
    formatter = jsonlogger.JsonFormatter()
    # Set the formatter
    logHandler.setFormatter(formatter)
    # Add the handler to the logger
    logger.addHandler(logHandler)

