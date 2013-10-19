from darkcloud.common.logger import Logger

from yaml import load
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

def ConfigObject(data):
    class ConfigObject(type(data)):
        def __init__(self, data):
            type(data).__init__(self, data)

        def host(self):
            try:
                return self.split(':')[0]
            except IndexError:
                return None
            except AttributeError:
                return None

        def port(self):
            try:
                return int(self.split(':')[1])
            except IndexError:
                return None
            except AttributeError:
                return None

        def ansi(self):
            return self.replace('\\e', '\033')

    return ConfigObject(data)

class Config(object):
    def __init__(self, filename):
        self._data = self._load_config(filename)

    def is_loaded(self):
        if self._data:
            return True
        else:
            return False

    def _load_config(self, filename):
        log = Logger('config')
        try:
            filepath = '/etc/darkcloud/%s.yml' % (filename)
            config_data = open(filepath).read()
            log.debug("Loaded configuration file '%s'" % (filepath))
        except:
            try:
                log.debug("Configuration not found at '%s'" % (filepath))

                filepath = 'config/%s.yml' % (filename)
                config_data = open(filepath).read()
                log.debug("Loaded configuration file '%s'" % (filepath))
            except:
                log.debug("Configuration not found at '%s'" % (filepath))
                log.critical("Can't load configuration file '%s'" % (filepath))
                return None
        return load(config_data)

    def __getitem__(self, key):
        try:
            return ConfigObject(self._data[key])
        except TypeError:
            return None
