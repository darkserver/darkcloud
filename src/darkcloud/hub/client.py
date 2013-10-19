import json

CLIENT_UNKNOWN = 0
CLIENT_ADMIN = 1
CLIENT_USER = 2
CLIENT_SERVER = 3

clients = []

class UnknownClientHash(Exception):
    def __init__(self, value):
        self.value = value

    def __unicode__(self):
        return repr(self.value)

class Client():
    def __init__(self, connection):
        self.connection = connection

        self.info = {}
        self.name = None

        self.type = CLIENT_UNKNOWN
        self.is_authorized = False

        # only for slave
        self.capabilities = []

    def authorize(self, client_type, login, password):
        if client_type == 'adm':
            if login == 'admin' and password == '1234':
                self.name = login
                self.type = CLIENT_ADMIN
                self._is_authorized = True
                return True

        elif client_type == 'slave':
            if password == 'imslave!':
                self.name = login
                self.type = CLIENT_SERVER
                self._is_authorized = True
                return True

        return False

    def __unicode__(self):
        return self.name

def find_client_by_addr(addr):
    for client in clients:
        if client.connection.remote_addr() == addr:
            return client

def add(connection):
    clients.append(Client(connection))
#    modify_hash(len(clients) - 1)
    return True

def modify(addr, data):
    for k,v in data.items():
        find_client_by_addr(addr)[k] = v
    return True

def remove(connection):
    clients.remove(find_client_by_addr(connection))
    return True

def _translate_group_to_int(group_name):
    group_assigns = {
        'admins': CLIENT_ADMIN,
        'users':  CLIENT_USER,
        'slaves': CLIENT_SERVER,
    }
    try:
        return group_assigns[group_name]
    except KeyError:
        return None

def _list(group):
    out = []

    for c in clients:
        if c.type == _translate_group_to_int(group):
            _x = {
                'name': c.name,
                'address': c.connection.remote_addr(),
            }
            if c.type == CLIENT_SERVER:
                _x['capabilities'] = c.capabilities
            out.append(_x)

    return out

def list_all(show = ['admins', 'users', 'slaves']):
    out = {}

    for s in show:
        out[s] = _list(s)

    return out
