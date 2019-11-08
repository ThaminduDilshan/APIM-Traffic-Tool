
# Copyright (c) 2019, WSO2 Inc. (http://www.wso2.org) All Rights Reserved.
#
# WSO2 Inc. licenses this file to you under the Apache License,
# Version 2.0 (the "License"); you may not use this file except
# in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied. See the License for the
# specific language governing permissions and limitations
# under the License.

import multiprocessing
import os
import pickle
import time
import yaml
from faker import Factory
import string
from datetime import datetime
from utils import util_methods
import ipaddress
import random
from utils.util_methods import generate_biased_random


def init(ctr):
    """
    Initialize globals variables in a process memory space when the process pool is created
    """
    global scenario_counter
    scenario_counter = ctr


def generate_unique_ip():
    """
    Returns a unique ip address
    :return: an unique ip
    """
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
    """
    generates a random cookie
    :return: a randomly generated cookie
    """
    letters_and_digits = string.ascii_lowercase + string.digits
    cookie = 'JSESSIONID='
    cookie += ''.join(random.choice(letters_and_digits) for ch in range(31))
    return cookie


def handler_scenario(scenario):
    """
    Execute scenarios from the scenario pool
    :param scenario: A list containing a scenario
    :return: none
    """
    global attack_duration, protocol, host, port, payloads, user_agents, start_time, max_request_multiplier, min_request_multiplier, pool

    if datetime.now().timestamp() <= start_time + attack_duration:
        print("Executing Scenario {}".format(scenario_counter.value))
        scenario_counter.value += 1
        context = scenario[1]
        version = scenario[2]
        resource_path = scenario[3]
        token = scenario[4]
        method = scenario[5]
        request_target = scenario[0] * random.randint(min_request_multiplier, max_request_multiplier)
        current_requests = 0
        ip = scenario[6]
        cookie = scenario[7]

        # if request target is more than 2

        request_path = "{}://{}:{}/{}/{}/{}".format(protocol, host, port, context, version, resource_path)
        random_user_agent = random.choice(user_agents)
        random_payload = random.choice(payloads)

        for i in range(request_target):
            if datetime.now().timestamp() <= start_time + attack_duration:
                response = util_methods.send_simple_request(request_path, method, token, ip, cookie, random_user_agent, payload=random_payload)
                request_string = "{},{},{},{},{},{},{}".format(datetime.now(), request_path, method, token, ip, cookie, response.status_code)
                util_methods.log_request("../../../../../../dataset/attack/abnormal_token.csv", request_string, "a")

                # print("Request sent with token: %s" % token, flush=True)

            time.sleep(generate_biased_random(0, 3, 2))
            current_requests += 1

    else:
        pool.terminate()


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
    max_request_multiplier = attack_config['attacks']['abnormal_token_usage']['max_request_multiplier']
    min_request_multiplier = attack_config['attacks']['abnormal_token_usage']['min_request_multiplier']
    fake_generator = Factory.create()
    current_ips = []

    start_time = datetime.now().timestamp()
    scenario_counter = multiprocessing.Value("i", 1)

    print("-------------------------------- Abnormal Token Usage Attack Started -------------------------------- ")
    util_methods.log_request("../../../../../../dataset/attack/abnormal_token.csv", "Timestamp, Request path, Method,Access Token, IP Address, Cookie, Response Code", "w")

    pool = multiprocessing.Pool(processes=20, initializer=init, initargs=[scenario_counter])
    while datetime.now().timestamp() <= start_time + attack_duration:
        pool.map(handler_scenario, scenario_pool)
    pool.close()
    pool.join()

    print("-------------------------------- Abnormal Token Usage Attack Finished -------------------------------- ")
