import darkcloud.hub.client as client
import darkcloud.hub.core as core
from darkcloud.common.hmac import HMAC
from darkcloud.common.request import RequestFramework

# decorators...
def needs_auth(fn):
    def wrapped(self, **kwargs):
        if 'client' in kwargs:
            if not kwargs['client'].is_authorized:
                return self.reply(401)
            return fn(self, **kwargs)
        return self.reply(401)
    return wrapped

# code
class Request(RequestFramework):
    def __init__(self, use_hmac=True):
        RequestFramework.__init__(self, use_hmac)

    def _get_client(self, addr):
        return client.find_client_by_addr(addr)

    def action_auth(self, **kwargs):
        if 'client' not in kwargs:
            return self.reply(500)

        if (kwargs['client'].authorize(kwargs['type'],
                                      kwargs['name'],
                                      kwargs['password'])):
            return self.reply(200, {'fullname': core.full_name,
                                    'name':     core.name,
                                    'version':  core.version})
        else:
            return self.reply(403)

    @needs_auth
    def action_list(self, **kwargs):
        return self.reply(200, client.list_all())
