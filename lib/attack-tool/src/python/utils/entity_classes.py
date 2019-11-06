
from collections import defaultdict

# To store user details
class User:
    def __init__(self, ip, token, cookie):
        self.ip = ip
        self.token = token
        self.cookie = cookie


# To store API details
class API:
    def __init__(self, protocol, host, port, context, version, name):
        self.protocol = protocol
        self.host = host
        self.port = port
        self.context = context
        self.name = name
        self.version = version
        self.resources = defaultdict(list)
        self.base_url = "{}://{}:{}/{}/{}".format(protocol, host, port, context, version)

    def add_resource(self, method, path):
        self.resources[method].append(path)

