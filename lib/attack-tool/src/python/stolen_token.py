
import multiprocessing

import os
import pickle
import time

import yaml
from faker import Factory
import string
import random
from datetime import datetime


from utils import util_methods

import ipaddress
import random

from utils.util_methods import generate_biased_random


def init(ctr, fg, time):
    """
    Initialize globals variables in a process memory space when the process pool is created

    """
    global counter, flag, start_time
    counter = ctr
    flag = fg
    start_time = time


def set_flag(val):
    """
    Set the flag value which is used for a exit condition for the script
    :param val: an integer value
    :return: none
    """
    flag.value = val


def generate_unique_ip():
    global fake_generator, current_ips
    # temp_ip = fake_generator.ipv4()
    random.seed()
    MAX_IPV4 = ipaddress.IPv4Address._ALL_ONES
    temp_ip = ipaddress.IPv4Address._string_from_ip_int(random.randint(0, MAX_IPV4))
    while temp_ip in current_ips:
        temp_ip = fake_generator.ipv4()

    current_ips.append(temp_ip)
    return temp_ip


def generate_cookie():
    letters_and_digits = string.ascii_lowercase + string.digits
    cookie = 'JSESSIONID='
    cookie += ''.join(random.choice(letters_and_digits) for ch in range(31))
    return cookie


def handler_time(scenario):
    global attack_duration, protocol, host, port, payloads, user_agents
    if datetime.now().timestamp() <= start_time.value + attack_duration:
        context = scenario[1]
        version = scenario[2]
        resource_path = scenario[3]
        token = scenario[4]
        method = scenario[5]
        request_target = scenario[0]
        current_requests = 0

        request_path = "{}://{}:{}/{}/{}/{}".format(protocol, host, port, context, version, resource_path)
        random_user_agent = random.choice(user_agents)
        random_ip = generate_unique_ip()
        random_cookie = generate_cookie()
        random_payload = random.choice(payloads)

        for i in range(request_target):
            if datetime.now().timestamp() <= start_time.value + attack_duration:
                response = util_methods.send_simple_request(request_path, method, token, random_ip, random_cookie, random_user_agent,payload=random_payload)
                request_string = "{},{},{},{},{},{},{}".format(datetime.now(), request_path, method, token, random_ip, random_cookie, response.status_code)
                util_methods.log_request("../../../../../../dataset/attack/stolen_token.csv", request_string, "a")
                counter.value += 1
                print("Request sent with token: %s" % token, flush=True)

            time.sleep(generate_biased_random(0, 5, 2))
            current_requests += 1


if __name__ == '__main__':
    with open(os.path.abspath(os.path.join(__file__, "../../../../traffic-tool/data/runtime_data/user_scenario_pool.sav")), "rb") as scenario_file:
        scenario_pool = pickle.load(scenario_file, )

    with open(os.path.abspath(os.path.join(__file__, "../../../../../config/apim.yaml")), "r") as config_file:
        config = yaml.load(config_file, Loader=yaml.FullLoader)

    with open(os.path.abspath(os.path.join(__file__, "../../../../../config/attack-tool.yaml")), "r") as attack_config_file:
        attack_config = yaml.load(attack_config_file, Loader=yaml.FullLoader)

    # configurations
    protocol = config['management_console']['protocol']
    host = config['management_console']['host']
    port = config['api_manager']['nio_pt_transport_port']
    attack_duration = attack_config['general_config']['attack_duration']

    payloads = attack_config['general_config']['payloads']
    user_agents = attack_config['general_config']['user_agents']

    fake_generator = Factory.create()
    current_ips = []

    #
    start_time = multiprocessing.Value('f', datetime.now().timestamp())
    counter = multiprocessing.Value('i', 0)
    flag = multiprocessing.Value('i', 0)

    #
    print("-------------------------------- Stolen Token Attack started -------------------------------- ")
    util_methods.log_request("../../../../../../dataset/attack/stolen_token.csv", "Timestamp, Request path, Method,Access Token, IP Address, Cookie, Response Code", "w")

    p = multiprocessing.Pool(processes=20, initializer=init, initargs=(counter, flag, start_time))
    while datetime.now().timestamp() <= start_time.value + attack_duration:
        p.map(handler_time, scenario_pool)
    p.close()
    p.join()

    print("-------------------------------- Stolen Token Attack Finished -------------------------------- ")
