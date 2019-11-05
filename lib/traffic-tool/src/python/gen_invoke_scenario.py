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
user_ip = {}
user_cookie = {}
users_apps = {}
scenario_pool = []

fake_generator = Factory.create()
abs_path = os.path.abspath(os.path.dirname(__file__))

with open(abs_path+'/../../../../config/traffic-tool.yaml', 'r') as file:
    traffic_config = yaml.load(file, Loader=yaml.FullLoader)
scenario_name = traffic_config['scenario_name']


'''
    This method will write the given log output to the log.txt file
'''
def log(tag, write_string):
    with open(abs_path+'/../../../../logs/traffic-tool.log', 'a+') as file:
        file.write("[{}] ".format(tag) + str(datetime.now()) + ": " + write_string + "\n")


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
    ip_list = []
    for ip in range(count):
        ip_list.append(ipGen())

    unique_list = list(set(ip_list))

    while( len(unique_list) != len(ip_list) ):
        diff = len(ip_list) - len(unique_list)

        for i in range(diff):
            unique_list.append(ipGen())
        unique_list = list(set(unique_list))

    return unique_list


'''
    This method will return a list of unique cookies
'''
def genUniqueCookieList(count:int):
    cookie_list = []
    for cookie in range(count):
        cookie_list.append(getCookie())

    unique_list = list(set(cookie_list))

    while( len(unique_list) != len(cookie_list) ):
        diff = len(cookie_list) - len(unique_list)

        for i in range(diff):
            unique_list.append(getCookie())
        unique_list = list(set(unique_list))

    return unique_list


'''
    Execute the script and generate the user scenario distribution
    Usage: python3 gen_invoke_scenario.py
    output folders: lib/traffic-tool/data/scenario/ and lib/traffic-tool/data/runtime_data/
'''

# generate a set of ips and cookies for each user
with open(abs_path+'/../../data/scenario/{}/data/user_generation.csv'.format(scenario_name)) as file:
    userlist = file.read().split('\n')

    ip_list = genUniqueIPList(len(userlist))
    cookie_list = genUniqueCookieList(len(userlist))

    for user in userlist:
        username = user.split('$$ ')[0]
        user_ip.update( {username: ip_list.pop()} )
        user_cookie.update( {username: cookie_list.pop()} )

# update dictionary for apps and their users
with open(abs_path+'/../../data/scenario/{}/data/app_creation.csv'.format(scenario_name)) as file:
    appList = file.read().split('\n')

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

# generate scenario data according to the script and append to the pool
with open(abs_path+'/../../data/scenario/{}/data/api_invoke_scenario.csv'.format(scenario_name)) as file:
    scenario_data = csv.reader(file, delimiter='$')

    for row in scenario_data:
        app_name = row[0]
        invokes = row[1]
        invokes = invokes.strip('][').split("],[")

        user_count = int(invokes[0].split(',')[0])
        users = []
        for i in range(user_count):
            users.append(users_apps.get(app_name).pop())

        for invoke in invokes:
            row2 = invoke.split(',')
            api_name = row2[1]
            method = row2[2]
            call_median = int(row2[3])
            path = row2[4]
            api_version = "1"
            full_path = api_name + "/" + api_version + "/" + path + "/"

            for user in users:              # user[username,token,ip,cookie]
                no_of_requests = varySlightly(call_median, user_count)
                scenario_pool.append([no_of_requests, api_name, "1", path, user[1], method, user[2], user[3], app_name, user[0]])

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
