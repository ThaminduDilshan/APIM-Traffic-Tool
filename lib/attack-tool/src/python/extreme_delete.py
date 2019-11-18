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

import os
import random
import time
from datetime import datetime
from multiprocessing.dummy import Pool

import pandas as pd
import yaml

from utils import util_methods
from utils.entity_classes import API
from utils.util_methods import generate_random_string


def request_handler(i):
    global attack_duration, protocol, host, port, payloads, user_agents, api_list, dataset_path

    up_time = datetime.now() - start_time
    if up_time.seconds < attack_duration:
        api = random.choice(api_list)
        context = api.context
        version = api.version
        resource_path = random.choice(api.resources['DELETE'])
        random_user = random.choice(api.users)
        token = random_user[0]
        method = "DELETE"

        # time.sleep(generate_biased_random(0, 10, 2))
        time.sleep(random.randint(0, 10))

        request_path = "{}://{}:{}/{}/{}/{}".format(protocol, host, port, context, version, resource_path)
        random_user_agent = random.choice(user_agents)
        ip = random_user[2]
        cookie = random_user[3]
        path_param = generate_random_string(10)

        response = util_methods.send_simple_request(request_path, method, token, ip, cookie, random_user_agent, path_params=path_param)

        request_info = "{},{},{},{},{},{},{}".format(datetime.now(), request_path, method, token, ip, cookie, response.status_code)
        util_methods.log(dataset_path, request_info, "a")

        print("Request sent with token: %s" % token, flush=True)


# Program Execution
if __name__ == '__main__':

    with open(os.path.abspath(os.path.join(__file__, "../../../../../config/apim.yaml")), "r") as config_file:
        config = yaml.load(config_file, Loader=yaml.FullLoader)

    with open(os.path.abspath(os.path.join(__file__, "../../../../../config/attack-tool.yaml")), "r") as attack_config_file:
        attack_config = yaml.load(attack_config_file, Loader=yaml.FullLoader)

    # reading configurations from attack-tool.yaml
    protocol = attack_config['general_config']['api_host']['protocol']
    host = attack_config['general_config']['api_host']['ip']
    port = attack_config['general_config']['api_host']['port']
    attack_duration = attack_config['general_config']['attack_duration']
    scenario_name = attack_config['general_config']['scenario']
    payloads = attack_config['general_config']['payloads']
    user_agents = attack_config['general_config']['user_agents']

    # reading api configuration from apim.yaml
    apis = config['apis']

    # reading user data (access token, api name,user ip, and cookie)
    user_details = pd.read_csv(os.path.abspath(os.path.join(__file__, "../../../../traffic-tool/data/scenario/{}/token_ip_cookie.csv".format(scenario_name))))
    user_details_groups = user_details.groupby('api_name')

    # Instantiating API objects which has delete methods and appending them to api_list
    api_list = []
    for api in apis:
        temp = API(protocol, host, port, api['context'], api['version'], api['name'])
        temp.users = user_details_groups.get_group(temp.name).values.tolist()
        for resource in api['resources']:
            temp.add_resource(resource['method'], resource['path'])
        if 'DELETE' in temp.resources.keys():
            api_list.append(temp)

    start_time = datetime.now()

    # Recording column names in the dataset csv file
    dataset_path = "../../../../../../dataset/attack/extreme_delete.csv"
    util_methods.log(dataset_path, "Timestamp, Request path, Method,Access Token, IP Address, Cookie, Response Code", "w")

    attack_tool_log_path = "../../../../../../logs/attack-tool.log"
    log_string = "[INFO] {} - Extreme delete attack started ".format(start_time)
    print(log_string)
    util_methods.log(attack_tool_log_path, log_string, "a")
    util_methods.log(dataset_path, "Timestamp, Request path, Method,Access Token, IP Address, Cookie, Response Code", "w")

    process_pool = Pool(processes=20)

    # Executing scenarios until the attack duration elapses
    while True:
        time_elapsed = datetime.now() - start_time
        if time_elapsed.seconds >= attack_duration:
            log_string = "[INFO] {} - Attack terminated successfully. Time elapsed: {} minutes".format(datetime.now(), time_elapsed.seconds / 60.0)
            print(log_string)
            util_methods.log(attack_tool_log_path, log_string, "a")
            break
        else:
            process_pool.map(request_handler, range(1000))

    # closes the process pool and wait for the processes to finish
    process_pool.close()
    process_pool.join()
