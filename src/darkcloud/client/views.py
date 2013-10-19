def list(data):
    if 'admins' in data:
        print("Connected admins:")
        for i in data['admins']:
            print("  \033[1;36m%-16s\033[0m %-15s" % (i['name'], i['address']))
        print("")

    if 'users' in data:
        print("Connected users:")
        for i in data['users']:
            print("  \033[1;36m%-16s\033[0m %-15s" % (i['name'], i['address']))
        print("")

    if 'slaves' in data:
        print("Connected servers:")
        for i in data['slaves']:
            print("  \033[1;36m%-32s\033[0m %-15s \033[0;33m%s\033[0m" % (i['name'], i['address'], ' '.join(i['capabilities'])))
        print("")
