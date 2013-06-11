CLIENT_UNKNOWN = 0
CLIENT_ADMIN = 1
CLIENT_USER = 2
CLIENT_SERVER = 3

clients = []

def add(connection):
    clients.append({
        'conn': connection,
        'address': connection.remote_addr(),
        'type': CLIENT_UNKNOWN,
        'info': {},
    })

    return True

def modify(addr, data):
    for c in clients:
        if c['address'] == addr:
            for k,v in data.items():
                c[k] = v
            return True

    return False

def remove(addr):
    try:
        for c in clients:
            if c['address'] == addr:
                clients.remove(c)
                return
    except ValueError:
        pass

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
        if c['type'] == _translate_group_to_int(group):
            out.append(c.copy())

    # remove connection socket
    # we can't transport this via json
    # and well... we don't even want to do this
    for x in out:
        x.pop('conn')

    return out

def list_all(show = ['admins', 'users', 'slaves']):
    out = {}

    for s in show:
        out[s] = _list(s)

    return out

def auth(addr, client_type, clientname, password):
    if client_type == "adm":
        if clientname == "admin" and password == "1234":
            return modify(addr, {
                'type'     : CLIENT_ADMIN,
                'address'  : addr,
                'username' : clientname,
            })

    elif client_type == "slave":
        if password == "imslave!":
            return modify(addr, {
                'type'     : CLIENT_SERVER,
                'address'  : addr,
                'hostname' : clientname,
            })

    return False

def authorized(addr):
    for c in clients:
        if addr == c['address']:
            return (c['type'], c)

    return (False, None)

def get_by_addr(addr):
    for c in clients:
        if addr == c['address']:
            if 'username' in c:
                return c['username']
            elif 'hostname' in c:
                return c['hostname']

    return '-unknown-'

def send(addr, data):
    for c in clients:
        if c['address'] == addr:
            c['conn'].send(data)
            return True
    return False

def send_to_all(data, category = ['admins', 'users', 'slaves']):
    for c in clients:
        if 'admins' in category and c['type'] == CLIENT_ADMIN:
            c['conn'].send(data)
        if 'users' in category and c['type'] == CLIENT_USER:
            c['conn'].send(data)
        if 'slaves' in category and c['type'] == CLIENT_SERVER:
            if c['state'] == 0:
                c['conn'].send(data)
    return True

def on_info(addr, data):
    for c in clients:
        if c['address'] == addr:
            for d in data:
                c['info'][d] = data[d]
