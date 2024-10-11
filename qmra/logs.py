import logging
import sys
from django.utils import log
import structlog


class ExcludeEventsFilter(logging.Filter):
    def __init__(self, excluded_event_type=None):
        super().__init__()
        self.excluded_event_type = excluded_event_type

    def filter(self, record):
        if not isinstance(record.msg, dict) or self.excluded_event_type is None:
            return True  # Include the log message if msg is not a dictionary or excluded_event_type is not provided

        if record.msg.get('event') in self.excluded_event_type:
            return False  # Exclude the log message
        return True  # Include the log message


no_error_filter = log.CallbackFilter(
    lambda r: not r.levelname == "ERROR"
)


def no_health(record):
    rqs = record.msg["request"]
    return not ("/health" in rqs or "/ready" in rqs or "/metrics" in rqs)


no_health_filter = log.CallbackFilter(no_health)


console_stdout_handler = {
    "class": "logging.StreamHandler",
    "formatter": "key_value",
    "level": "INFO",
    "filters": [no_error_filter, no_health_filter],
    "stream": "ext://sys.stdout"
}

console_stderr_handler = {
    "class": "logging.StreamHandler",
    "formatter": "key_value",
    "level": "ERROR",
    "stream": "ext://sys.stderr"
}

json_stdout_handler = {
    "class": "logging.StreamHandler",
    "formatter": "json_formatter",
    "filters": [no_error_filter, no_health_filter],
    "stream": "ext://sys.stdout"
}

json_stderr_handler = {
    "class": "logging.StreamHandler",
    "formatter": "json_formatter",
    "filters": [no_error_filter, no_health_filter],
    "stream": "ext://sys.stderr"
}