
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

import csv
import random
import string
import requests
import time
from datetime import datetime
from faker import Factory
import sys
import argparse
import urllib3
import pickle
import yaml
import os
import json
import math
from multiprocessing.dummy import Pool as ThreadPool


urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

parser = argparse.ArgumentParser("run traffic tool")
parser.add_argument("filename", help="Enter a filename to write final output", type=str)
parser.add_argument("runtime", help="Enter the script execution time in minutes", type=float)
args = parser.parse_args()
filename = args.filename + ".csv"
script_runtime = args.runtime * 60       # in seconds

# Variables
no_of_processes = None
max_connection_refuse_count = None
host_protocol = None
host_ip = None
host_port = None
heavy_traffic = None
scenario_name = None
post_data = None

script_starttime = None
scenario_pool = []
connection_refuse_count = 0
active_processes = 0
process_pool = []

fake_generator = Factory.create()
abs_path = os.path.abspath(os.path.dirname(__file__))


'''
    This method will load and set the configuration data
'''
def loadConfig():
    global no_of_processes, max_connection_refuse_count, host_protocol, host_ip, host_port, heavy_traffic, scenario_name, post_data

    with open(abs_path+'/../../../../config/traffic-tool.yaml', 'r') as file:
        traffic_config = yaml.load(file, Loader=yaml.FullLoader)

    no_of_processes = int(traffic_config['tool_config']['no_of_processes'])
    max_connection_refuse_count = int(traffic_config['tool_config']['max_connection_refuse_count'])
    heavy_traffic = str(traffic_config['tool_config']['heavy_traffic']).lower()
    host_protocol = traffic_config['api_host']['protocol']
    host_ip = traffic_config['api_host']['ip']
    host_port = traffic_config['api_host']['port']
    scenario_name = traffic_config['scenario_name']
    post_data = traffic_config['api']['payload']


'''
    This method will write the given log output to the log.txt file
'''
def log(tag, write_string):
    with open(abs_path+'/../../../../logs/traffic-tool.log', 'a+') as file:
        file.write("[{}] ".format(tag) + str(datetime.now()) + ": " + write_string + "\n")


'''
    This method will send http requests to the given address: GET, POST only
'''
def sendRequest(url_protocol, url_ip, url_port, api_name, api_version, path, access_token, method, user_ip, cookie, app_name, username,user_agent):
    url = "{}://{}:{}/{}/{}/{}".format(url_protocol, url_ip, url_port, api_name, api_version, path)
    headers = {
        'accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': 'Bearer {}'.format(access_token),
        'client-ip': '{}'.format(user_ip),
        'x-forwarded-for': '{}'.format(user_ip),
        'cookie': '{}'.format(cookie),
        'User-Agent': user_agent
    }
    code = None
    res_txt = ""

    try:
        if method=="GET":
            response = requests.get(url=url, headers=headers, verify=False)
            code = response.status_code
            res_txt = response.text
        elif method=="POST":
            data = json.dumps(post_data)
            response = requests.post(url=url, headers=headers, data=data, verify=False)
            code = response.status_code
            res_txt = response.text
        else:
            code = '400'
            res_txt = 'Invalid type!'
    except ConnectionRefusedError:
        log("ERROR", "HTTP Connection Refused!")
        code = '404'
    except Exception as e:
        log("ERROR", str(e))
        code = '404'

    # write data to files
    write_string = ""

    # user agent is wrapped around quotes because there are commas in the user agent and they clash with the commas in csv file
    write_string = str(datetime.now()) + "," + api_name + "," + access_token + "," + user_ip + "," + cookie + "," + api_name+"/"+api_version+"/"+path + "," + method + "," + str(code) +",\"" + user_agent +"\"\n"
    with open(abs_path+'/../../../../dataset/traffic/{}'.format(filename), 'a+') as file:
        file.write(write_string)

    return code,res_txt


'''
    This method will return a random integer between zero and eight.
    Highly biased for returning zero.
'''
def randomSleepTime():
    min = 0
    max = 8
    exp = 5
    return math.floor(min + (max - min) * pow(random.random(), exp))


'''
    This method will take a given invoke scenario and execute it.
    Supposed to be executed from a process.
'''
def runInvoker(scenario_row):
    global connection_refuse_count, script_starttime, script_runtime, active_processes

    no_of_requests = scenario_row[0] - random.randint(0, scenario_row[0])
    api_name = scenario_row[1]
    api_version = scenario_row[2]
    path = scenario_row[3]
    access_token = scenario_row[4]
    method = scenario_row[5]
    user_ip = scenario_row[6]
    cookie = scenario_row[7]
    app_name = scenario_row[8]
    username = scenario_row[9]
    user_agent = scenario_row[10]

    for i in range(no_of_requests):
        try:
            res_code, res_txt = sendRequest(host_protocol, host_ip, host_port, api_name, api_version, path, access_token, method, user_ip, cookie, app_name, username,user_agent)
            if heavy_traffic != 'true':
                time.sleep(randomSleepTime())
        except:
            connection_refuse_count += 1
            if connection_refuse_count > max_connection_refuse_count:
                log("ERROR", "Terminating the process due to maximum no of connection refuses!")
                active_processes -= 1
                sys.exit()

        up_time = datetime.now() - script_starttime
        if up_time.seconds >= script_runtime:
            active_processes -= 1
            break


'''
    Execute the scenario and generate the dataset
    Usage: python3 invoke_API.py filename exectime
    output folder: dataset/traffic/
'''

# load and set tool configurations
loadConfig()

with open(abs_path+'/../../../../dataset/traffic/{}'.format(filename), 'w') as file:
    file.write("timestamp,api,access_token,ip_address,cookie,invoke_path,http_method,response_code,user agent\n")

# load and set the scenario pool
scenario_pool = pickle.load(open(abs_path+"/../../data/runtime_data/user_scenario_pool.sav", "rb"))

# shuffle the pool
random.shuffle(scenario_pool)

# record script starttime
script_starttime = datetime.now()

pool = ThreadPool(no_of_processes)

print("[INFO] Scenario loaded successfully. Wait {} minutes to complete the script!".format(str(script_runtime/60)))
log("INFO", "Scenario loaded successfully. Wait {} minutes to complete the script!".format(str(script_runtime/60)))

while True:
    time_elapsed = datetime.now() - script_starttime
    if time_elapsed.seconds >= script_runtime:
        print("[INFO] Script terminated successfully. Time elapsed: {} minutes".format(time_elapsed.seconds/60.0))
        log("INFO", "Script terminated successfully. Time elapsed: {} minutes".format(time_elapsed.seconds/60.0))
        break
    else:
        pool.map(runInvoker, scenario_pool)

pool.close()
pool.join()
