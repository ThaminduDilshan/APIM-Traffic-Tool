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
import sys
from multiprocessing.dummy import Pool
import os
import pickle
import time

import requests
import yaml
import string
from datetime import datetime
from utils import util_methods
import ipaddress
import random
import numpy as np
from utils.util_methods import generate_biased_random


def generate_unique_ip():
    """
    Returns a unique ip address
    :return: an unique ip
    """
    global used_ips

    random.seed()
    MAX_IPV4 = ipaddress.IPv4Address._ALL_ONES
    temp_ip = ipaddress.IPv4Address._string_from_ip_int(random.randint(0, MAX_IPV4))
    while temp_ip in used_ips:
        temp_ip = ipaddress.IPv4Address._string_from_ip_int(random.randint(0, MAX_IPV4))

    used_ips.append(temp_ip)
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


def execute_scenario(scenario):
    """
    Execute a scenario from the scenario pool to simulate the usage of a stolen token
    :param scenario: A list containing a scenario
    :return: none
    """
    global attack_duration, protocol, host, port, payloads, user_agents, start_time, dataset_path

    up_time = datetime.now() - start_time

    if up_time.seconds < attack_duration:
        request_target = scenario[0]
        context = scenario[1]
        version = scenario[2]
        resource_path = scenario[3]
        token = scenario[4]
        method = scenario[5]

        request_path = "{}://{}:{}/{}/{}/{}".format(protocol, host, port, context, version, resource_path)
        random_user_agent = random.choice(user_agents)
        random_ip = generate_unique_ip()
        random_cookie = generate_cookie()
        random_payload = random.choice(payloads)
        accept = content_type = "application/json"

        for i in range(request_target):
            up_time = datetime.now() - start_time
            if up_time.seconds >= attack_duration:
                break
            try:
                response = util_methods.send_simple_request(request_path, method, token, random_ip, random_cookie, accept, content_type, random_user_agent, payload=random_payload)
                request_info = "{},{},{},{},{},{},{},{},{},\"{}\",{}".format(datetime.now(), random_ip, token, method, request_path, random_cookie, accept, content_type, random_ip, random_user_agent,
                                                                             response.status_code,
                                                                             )
                util_methods.log(dataset_path, request_info, "a")
            except requests.exceptions.RequestException:
                msg_string = "[Error] {} - Request Failure\n\t {}".format(datetime.now(), str(ex))
                print(msg_string)
                util_methods.log(attack_tool_log_path, msg_string, "a")

            # sleep the process for a random period of time between 0 and 5 seconds but biased to 0
            time.sleep(abs(int(np.random.normal() * 10)))


# Program Execution
if __name__ == '__main__':

    attack_tool_log_path = "../../../../../../logs/attack-tool.log"

    try:
        with open(os.path.abspath(os.path.join(__file__, "../../../../traffic-tool/data/runtime_data/user_scenario_pool.sav")), "rb") as scenario_file:
            scenario_pool = pickle.load(scenario_file, )

        with open(os.path.abspath(os.path.join(__file__, "../../../../../config/attack-tool.yaml")), "r") as attack_config_file:
            attack_config = yaml.load(attack_config_file, Loader=yaml.FullLoader)
    except FileNotFoundError as ex:
        error_string = "[ERROR] {} - {}: \'{}\'".format(datetime.now(), ex.strerror, ex.filename)
        print(error_string)
        util_methods.log(attack_tool_log_path, error_string, "a")
        sys.exit()

    # Reading configurations from attack-tool.yaml
    protocol = attack_config['general_config']['api_host']['protocol']
    host = attack_config['general_config']['api_host']['ip']
    port = attack_config['general_config']['api_host']['port']
    attack_duration = attack_config['general_config']['attack_duration']
    payloads = attack_config['general_config']['payloads']
    user_agents = attack_config['general_config']['user_agents']
    process_count = attack_config['general_config']['number_of_processes']

    # Recording column names in the dataset csv file
    dataset_path = "../../../../../../dataset/attack/stolen_token.csv"
    util_methods.log(dataset_path, "timestamp,ip_address,access_token,http_method,invoke_path,cookie,accept,content_type,x_forwarded_for,user_agent,response_code", "w")

    used_ips = []
    start_time = datetime.now()

    log_string = "[INFO] {} - Stolen token attack started ".format(start_time)
    print(log_string)
    util_methods.log(attack_tool_log_path, log_string, "a")

    process_pool = Pool(processes=process_count)

    # Executing scenarios until the attack duration elapses
    while True:
        time_elapsed = datetime.now() - start_time
        if time_elapsed.seconds >= attack_duration:
            log_string = "[INFO] {} - Attack terminated successfully. Time elapsed: {} minutes".format(datetime.now(), time_elapsed.seconds / 60.0)
            print(log_string)
            util_methods.log(attack_tool_log_path, log_string, "a")
            break
        else:
            process_pool.map(execute_scenario, scenario_pool)

    # closes the process pool and wait for the processes to finish
    process_pool.close()
    process_pool.join()
