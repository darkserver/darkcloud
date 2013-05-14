class HMAC():
    def __init__(self):
        pass

    def sign_message(self, session_id, private_key, message):
        return "1234567890abcdef %s" % message

    def compare(self, msg_hash, msg):
        if msg_hash == '1234567890abcdef':
            return True
        else:
            return False
