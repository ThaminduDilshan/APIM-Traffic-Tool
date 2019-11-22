
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
import pickle
from faker import Factory
import yaml
import os
from datetime import datetime

# Variables
scenario_name = None
apis = None
invoke_scenario = None
user_ip = {}
user_cookie = {}
users_apps = {}
scenario_pool = []
existing_no_of_user_combinations = 0         # to validate the user count
total_no_of_user_combinations = 0

fake_generator = Factory.create()

# setup configurations
abs_path = os.path.abspath(os.path.dirname(__file__))

with open(abs_path+'/../../../../config/traffic-tool.yaml', 'r') as file:
    traffic_config = yaml.load(file, Loader=yaml.FullLoader)
scenario_name = traffic_config['scenario_name']

with open(abs_path+'/../../../../config/apim.yaml', 'r') as file:
    apim_config = yaml.load(file, Loader=yaml.FullLoader)
apis = apim_config['apis']


'''
    This method will write the given log output to the log.txt file
'''
def log(tag, write_string):
    with open(abs_path+'/../../../../logs/traffic-tool.log', 'a+') as file:
        file.write("[{}] ".format(tag) + str(datetime.now()) + ": " + write_string + "\n")


'''
    This method will return the invoke path for a given api and http method
'''
def getPath(api_name, method):
    global apis

    for api in apis:
        if api.get('name') == api_name:
            context = str(api.get('context'))
            version = str(api.get('version'))
            resources = api.get('resources')
            for resource in resources:
                if resource.get('method') == method:
                    return context + '/' + version + '/' + str(resource.get('path'))


'''
    This method will return an integer slightly varied to the given median
'''
def varySlightly(median, no_of_users):
    lower_bound = int(median) - int(int(no_of_users)/2)
    upper_bound = int(median) + int(int(no_of_users)/2)
    if lower_bound <= 0:
        lower_bound = 1
    req_count = random.randint(lower_bound,upper_bound)

    return req_count


'''
    This method will return a randomly generated ipv4 address
'''
def ipGen():
    return fake_generator.ipv4()


'''
    This method will return a randomly generated cookie
'''
def getCookie():
    lettersAndDigits = string.ascii_lowercase + string.digits
    cookie = 'JSESSIONID='
    cookie += ''.join( random.choice(lettersAndDigits) for ch in range(31) )
    return cookie


'''
    This method will return a list of unique ipv4 addresses
'''
def genUniqueIPList(count:int):
    ip_list = set()
    while len(ip_list) != count:
        ip_list.add(ipGen())

    return list(ip_list)


'''
    This method will return a list of unique cookies
'''
def genUniqueCookieList(count:int):
    cookie_list = set()
    while len(cookie_list) != count:
        cookie_list.add(getCookie())

    return list(cookie_list)


'''
    Execute the script and generate the user scenario distribution
    Usage: python3 gen_invoke_scenario.py
    output folders: lib/traffic-tool/data/scenario/ and lib/traffic-tool/data/runtime_data/
'''

# generate a set of ips and cookies for each user
with open(abs_path+'/../../data/scenario/{}/data/user_generation.csv'.format(scenario_name)) as file:
    userlist = file.readlines()

    ip_list = genUniqueIPList(len(userlist))
    cookie_list = genUniqueCookieList(len(userlist))

    for user in userlist:
        username = user.split('$$ ')[0]
        user_ip.update( {username: ip_list.pop()} )
        user_cookie.update( {username: cookie_list.pop()} )

# update dictionary for apps and their users
with open(abs_path+'/../../data/scenario/{}/data/app_creation.csv'.format(scenario_name)) as file:
    appList = file.readlines()

    for app in appList:
        if app != "":
            appName = app.split('$ ')[0]
            users_apps.update( {appName: []} )

# set ips with username, access tokens and append to relevant lists
with open(abs_path+'/../../data/scenario/{}/api_invoke_tokens.csv'.format(scenario_name)) as file:
    user_token = csv.reader(file)

    for row in user_token:
        username = row[0]
        app_name = row[1]
        token = row[2]
        ip = user_ip.get(username)
        cookie = user_cookie.get(username)

        (users_apps[app_name]).append([username,token,ip,cookie])
        existing_no_of_user_combinations += 1

# generate scenario data according to the script and append to the pool
with open(abs_path+'/../../data/scenario/{}/data/invoke_scenario.yaml'.format(scenario_name)) as file:
    invoke_scenario = yaml.load(file, Loader=yaml.FullLoader)
scenario_data = invoke_scenario['invoke_scenario']

for item in scenario_data:
    app_name = item.get('app_name')
    user_count = int(item.get('no_of_users'))
    time_pattern = item.get('time_pattern')
    invokes = item.get('api_calls')

    # check whether the user count is valid (not more than the created number of users)
    total_no_of_user_combinations += user_count
    if total_no_of_user_combinations > existing_no_of_user_combinations:
        # invalid no of users (cannot execute the scenario)
        log("ERROR", "Invalid number of user count declared in 'invoke_scenario.yaml'. Expected {} users. Found {} or more.".format(existing_no_of_user_combinations, total_no_of_user_combinations))
        raise ArithmeticError("Invalid number of user count declared in 'invoke_scenario.yaml'. Expected {} users. Found {} or more.".format(existing_no_of_user_combinations, total_no_of_user_combinations))

    users = []
    for i in range(user_count):
        users.append(users_apps.get(app_name).pop())

        for invoke in invokes:
            api_name = invoke.get('api')
            method = invoke.get('method')
            call_median = int(invoke.get('no_of_requests'))
            full_path = getPath(api_name, method)

            for user in users:              # user[username,token,ip,cookie]
                no_of_requests = varySlightly(call_median, user_count)
                scenario_pool.append([no_of_requests, api_name, full_path, user[1], method, user[2], user[3], app_name, user[0], time_pattern])

# save scenario data
write_str = "access_token,api_name,ip_address,user_cookie\n"

for row in scenario_pool:
    api_name = row[1]
    access_token = row[4]
    ip_address = row[6]
    user_cookie = row[7]
    write_str += access_token + ',' + api_name + ',' + ip_address + ',' + user_cookie + "\n"

with open(abs_path+'/../../data/scenario/{}/token_ip_cookie.csv'.format(scenario_name), 'w') as file:
    file.write(write_str)

# saving scenario pool to a pickle file
pickle.dump(scenario_pool, open(abs_path+"/../../data/runtime_data/user_scenario_pool.sav", "wb"))

log("INFO", "User scenario distribution generated successfully")
print("User scenario distribution generated successfully")
