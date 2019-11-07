import multiprocessing
import os
import pickle
import random
import time
from datetime import datetime
import yaml
import pandas as pd

from utils import util_methods
from utils.entity_classes import API
from utils.util_methods import generate_random_string, generate_biased_random


def init(ctr, time):
    """
    Initialize globals variables in a process memory space when the process pool is created
    """
    global counter, flag, start_time
    counter = ctr
    start_time = time


def handler_time(i):
    global attack_duration, protocol, host, port, payloads, user_agents, api_list
    if datetime.now().timestamp() <= start_time.value + attack_duration:
        api = random.choice(api_list)
        context = api.context
        version = api.version
        resource_path = random.choice(api.resources['DELETE'])
        random_user = random.choice(api.users)
        token = random_user[0]
        method = "DELETE"
        current_requests = 0

        request_path = "{}://{}:{}/{}/{}/{}".format(protocol, host, port, context, version, resource_path)
        random_user_agent = random.choice(user_agents)
        ip = random_user[2]
        cookie = random_user[3]
        path_params = generate_random_string(10)

        # for i in range(request_target):
        #     if datetime.now().timestamp() <= start_time.value + attack_duration:
        response = util_methods.send_simple_request(request_path, method, token, ip, cookie, random_user_agent, path_params=path_params)
        request_string = "{},{},{},{},{},{},{}".format(datetime.now(), request_path, method, token, ip, cookie, response.status_code)
        util_methods.log_request("../../../../../../dataset/attack/extreme_delete.csv", request_string, "a")
        counter.value += 1
        print("Request sent with token: %s" % token, flush=True)

        time.sleep(generate_biased_random(0, 5, 2))
        current_requests += 1


if __name__ == '__main__':

    with open(os.path.abspath(os.path.join(__file__, "../../../../../config/apim.yaml")), "r") as config_file:
        config = yaml.load(config_file, Loader=yaml.FullLoader)

    with open(os.path.abspath(os.path.join(__file__, "../../../../../config/attack-tool.yaml")), "r") as attack_config_file:
        attack_config = yaml.load(attack_config_file, Loader=yaml.FullLoader)

    # configurations
    protocol = config['management_console']['protocol']
    host = config['management_console']['host']
    port = config['api_manager']['nio_pt_transport_port']
    attack_duration = attack_config['general_config']['attack_duration']
    scenario_name = attack_config['general_config']['scenario']
    payloads = attack_config['general_config']['payloads']
    user_agents = attack_config['general_config']['user_agents']
    apis = config['apis']

    #
    api_list = []

    # user data
    user_details = pd.read_csv(os.path.abspath(os.path.join(__file__, "../../../../traffic-tool/data/scenario/{}/token_ip_cookie.csv".format(scenario_name))))
    user_details_groups = user_details.groupby('api_name')

    # Instantiating API objects which has delete methods
    for api in apis:
        temp = API(protocol, host, port, api['context'], api['version'], api['name'])
        temp.users = user_details_groups.get_group(temp.name).values.tolist()
        for resource in api['resources']:
            temp.add_resource(resource['method'], resource['path'])
        if 'DELETE' in temp.resources.keys():
            api_list.append(temp)

    # fake_generator = Factory.create()
    # current_ips = []

    #
    start_time = multiprocessing.Value('f', datetime.now().timestamp())
    counter = multiprocessing.Value('i', 0)
    flag = multiprocessing.Value('i', 0)

    print("-------------------------------- Extreme Delete Attack started -------------------------------- ")
    util_methods.log_request("../../../../../../dataset/attack/extreme_delete.csv", "Timestamp, Request path, Method,Access Token, IP Address, Cookie, Response Code", "w")

    p = multiprocessing.Pool(processes=20, initializer=init, initargs=(counter, start_time))
    while datetime.now().timestamp() <= start_time.value + attack_duration:
        p.map(handler_time, range(1000))
    p.close()
    p.join()

    print("-------------------------------- Extreme Delete Attack Finished -------------------------------- ")
