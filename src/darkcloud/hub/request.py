import darkcloud.hub.client as client
import darkcloud.hub.core as core
from darkcloud.common.hmac import HMAC
from darkcloud.common.request import RequestFramework

# decorators...
def needs_auth(fn):
    def wrapped(self, **kwargs):
        if 'remote_addr' in kwargs:
            isauth, cl = client.authorized(kwargs['remote_addr'])
            if isauth == client.CLIENT_ADMIN:
                if 'data' in kwargs:
                    return fn(self, kwargs['data'])
                else:
                    return self.reply(500)
        return self.reply(401)
    return wrapped

# code
class Request(RequestFramework):
    def __init__(self, use_hmac = True):
        RequestFramework.__init__(self, use_hmac)

        self.cmds = {
            'auth' : 'auth',
            'list' : 'list',
        }

    def _parse_auth(self, data, **kwargs):
        if 'remote_addr' in kwargs and client.auth(kwargs['remote_addr'], data[0], data[1], data[2]):
            return self.reply(200, {'fullname' : core.full_name, 'name' : core.name, 'version' : core.version})
        else:
            return self.reply(403)

    @needs_auth
    def _parse_list(self, data, **kwargs):
        if len(data) > 1:
            return self.reply(200, client.list_all([data[1]]))
        else:
            return self.reply(200, client.list_all())

    def set_info(self, data):
        if 'caps' in data:
            print data['caps']
