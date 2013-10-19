import datetime
import sys

class Logger():
    def __init__(self, label=""):
        self._label = label
        self._format = "%(timestamp)s [%(label)12s] %(level)-6s %(message)s\033[0m"

    def _log(self, level, message):
        if level == 'CRIT':
            sys.stdout.write("\033[1;31m")
        elif level == 'WARN':
            sys.stdout.write("\033[1;33m")
        elif level == 'NOTICE':
            sys.stdout.write("\033[1;36m")

        print(self._format % {
            'timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'label': self._label,
            'level': level,
            'message': message,
        })

    def debug(self, message):
        self._log('DEBUG', message)

    def notice(self, message):
        self._log('NOTICE', message)

    def info(self, message):
        self._log('INFO', message)

    def warningl(self, message):
        self._log('WARN', message)

    def critical(self, message):
        self._log('CRIT', message)
