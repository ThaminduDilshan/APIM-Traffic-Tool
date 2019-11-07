import json
import math
import os
import time
from collections import defaultdict
from datetime import datetime
import random

import requests
# disabling warnings
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)


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


def send_simple_request(request_path, method, token, ip, cookie, user_agent, path_params=None, query_params=None, payload=None):
    """
    Send HTTP/HTTPS requests to a given API with the data in the DOSAttackData class
    :param num:
    :return: response code or done
    """

    code = 0

    if path_params is not None:
        request_path += "/{}".format(path_params)
    elif query_params is not None:
        request_path += "?{}".format(query_params)

    if payload is not None:
        request_body = payload
    else:
        request_body = generate_random_json()

    header_data = {
        'User-Agent': user_agent,
        'accept': 'application/json',
        'client-ip': '{}'.format(ip),
        'x-forwarded-for': '{}'.format(ip),
        'cookie': '{}'.format(cookie),
        'Authorization': 'Bearer {}'.format(token),
        'Content-Type': 'application/json'
    }
    r = requests.Response()

    try:
        if method == 'GET':
            r = requests.get(url=request_path, headers=header_data, timeout=(15, 30), verify=False)
        elif method == 'POST':
            r = requests.post(url=request_path, headers=header_data, data=request_body, timeout=(15, 30), verify=False)
        elif method == 'PUT':
            r = requests.put(url=request_path, headers=header_data, data=request_body, timeout=(15, 30), verify=False)
        elif method == 'DELETE':
            r = requests.delete(url=request_path, headers=header_data, timeout=(15, 30), verify=False)
        elif method == 'PATCH':
            r = requests.patch(url=request_path, headers=header_data, data=request_body, timeout=(15, 30), verify=False)

        return r

    except Exception as e:
        print(str(e))


def generate_biased_random(min, max, exp):
    return math.floor(min + (max - min) * pow(random.random(), exp))
