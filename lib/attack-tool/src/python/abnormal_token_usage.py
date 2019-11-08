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

from multiprocessing.dummy import Pool
import os
import pickle
import time
import yaml
from datetime import datetime
from utils import util_methods
import ipaddress
import random
from utils.util_methods import generate_biased_random


def handler_scenario(scenario):
    """
    Execute scenarios from the scenario pool
    :param scenario: A list containing a scenario
    :return: none
    """
    global attack_duration, protocol, host, port, payloads, user_agents, start_time, max_request_multiplier, min_request_multiplier,dataset_path
    up_time = datetime.now() - start_time
    if up_time.seconds < attack_duration:

        context = scenario[1]
        version = scenario[2]
        resource_path = scenario[3]
        token = scenario[4]
        method = scenario[5]
        request_target = scenario[0] * random.randint(min_request_multiplier, max_request_multiplier)
        current_requests = 0
        ip = scenario[6]
        cookie = scenario[7]

        request_path = "{}://{}:{}/{}/{}/{}".format(protocol, host, port, context, version, resource_path)
        random_user_agent = random.choice(user_agents)
        random_payload = random.choice(payloads)

        for i in range(request_target):
            up_time = datetime.now() - start_time
            if up_time.seconds >= attack_duration:
                break
            response = util_methods.send_simple_request(request_path, method, token, ip, cookie, random_user_agent, payload=random_payload)
            request_string = "{},{},{},{},{},{},{}".format(datetime.now(), request_path, method, token, ip, cookie, response.status_code)
            util_methods.log(dataset_path, request_string, "a")

            time.sleep(generate_biased_random(0, 3, 2))
            current_requests += 1


if __name__ == '__main__':

    with open(os.path.abspath(os.path.join(__file__, "../../../../traffic-tool/data/runtime_data/user_scenario_pool.sav")), "rb") as scenario_file:
        scenario_pool = pickle.load(scenario_file, )

    with open(os.path.abspath(os.path.join(__file__, "../../../../../config/apim.yaml")), "r") as config_file:
        config = yaml.load(config_file, Loader=yaml.FullLoader)

    with open(os.path.abspath(os.path.join(__file__, "../../../../../config/attack-tool.yaml")), "r") as attack_config_file:
        attack_config = yaml.load(attack_config_file, Loader=yaml.FullLoader)

    # configurations
    protocol = attack_config['general_config']['api_host']['protocol']
    host = attack_config['general_config']['api_host']['ip']
    port = attack_config['general_config']['api_host']['port']
    attack_duration = attack_config['general_config']['attack_duration']
    payloads = attack_config['general_config']['payloads']
    user_agents = attack_config['general_config']['user_agents']
    max_request_multiplier = attack_config['attacks']['abnormal_token_usage']['max_request_multiplier']
    min_request_multiplier = attack_config['attacks']['abnormal_token_usage']['min_request_multiplier']

    start_time = datetime.now()
    attack_tool_log_path = "../../../../../../logs/attack-tool.log"
    dataset_path = "../../../../../../dataset/attack/abnormal_token.csv"

    log_string = "[INFO] {} - Abnormal token usage attack started ".format(start_time)
    print(log_string)
    util_methods.log(attack_tool_log_path, log_string, "a")
    util_methods.log(dataset_path, "Timestamp, Request path, Method,Access Token, IP Address, Cookie, Response Code", "w")

    pool = Pool(processes=20)

    while True:
        time_elapsed = datetime.now() - start_time
        if time_elapsed.seconds >= attack_duration:
            log_string = "[INFO] {} - Attack terminated successfully. Time elapsed: {} minutes".format(datetime.now(),time_elapsed.seconds / 60.0)
            print(log_string)
            util_methods.log(attack_tool_log_path, log_string, "a")
            break
        else:
            pool.map(handler_scenario, scenario_pool)

    pool.close()
    pool.join()
