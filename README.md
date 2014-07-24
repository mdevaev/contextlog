contextlog
==========

Context-based logger and formatter


###Example###
```
import logging
import logging.config
import contextlog
import yaml

logging.config.dictConfig(yaml.load("""
version: 1
disable_existing_loggers: false
loggers:
    test:
        level: DEBUG
        handlers: [default]
formatters:
    default:
        (): contextlog.PartialFormatter
        style: "{"
        format: "{yellow}{asctime} {log_color}{levelname:>7} {purple}{name:20.20}{reset} CTX={ctx} {message}"
handlers:
    default:
        level: DEBUG
        class: logging.StreamHandler
        formatter: default
root:
    level: DEBUG
    handlers: [default]
"""))

log = contextlog.get_logger(__name__, ctx="test")
log.info("Message #1")

def method():
    bar = 1
    log = contextlog.get_logger(__name__)
    log.debug("Message #2")
    try:
        raise RuntimeError
    except:
        log.exception("Exception")
method()
```
Results:
```
$ python3 foo.py
2014-07-24 20:50:18,402    INFO __main__             CTX=test Message #1
2014-07-24 20:50:18,403   DEBUG __main__             CTX=test Message #2
2014-07-24 20:50:18,403   ERROR __main__             CTX=test Exception
Traceback (most recent call last):
  File "foo.py", line 36, in method
    raise RuntimeError
RuntimeError

Locals at innermost frame:

{'__logger_context': {'ctx': 'test'},
 'bar': 1,
 'log': <contextlog._ContextLogger object at 0x7f91d7b80860>}
```
