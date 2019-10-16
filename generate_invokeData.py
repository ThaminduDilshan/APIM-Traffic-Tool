import csv
import random
import string
from faker import Factory
import datetime
import argparse
from datetime import datetime as dt

# Variables
user_ip = {}
user_cookie = {}
users_apps = {}

fake_generator = Factory.create()

parser = argparse.ArgumentParser("generate traffic data")
parser.add_argument("filename", help="Enter a filename to write final output", type=str)
args = parser.parse_args()
filename = args.filename + ".csv"


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
    # return "{}.{}.{}.{}".format(random.randint(1,255), random.randint(0,255), random.randint(0,255), random.randint(0,255))
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

    # writing list of ips to a file
    ip_all_str = "ip_address\n"
    for ip in unique_list:
        ip_all_str += ip + "\n"
    with open('dataset/generated/ip_list_{}'.format(filename), 'w') as file:
        file.write(ip_all_str)

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
    This method will generate a random time stamp list for a given number of invokes
'''
def genTimeList(starttime, no_of_invokes:int):
    timestamps = []
    current = starttime
    # starttime = datetime.datetime(starttime)
    for i in range(no_of_invokes):
        current += datetime.timedelta(minutes=random.randrange(int(55/no_of_invokes)+5), seconds=random.randrange(40))
        timestamps.append(current)

    return timestamps


'''
    Execute the scenario and generate the dataset
    Usage: python3 generate_invokeData.py
    output folder: dataset/generated/
'''

# generate set of ips and cookies for each user
with open('APIM_scenario/data/user_generation.csv') as file:
    userlist = file.read().split('\n')

    ip_list = genUniqueIPList(len(userlist))
    cookie_list = genUniqueCookieList(len(userlist))

    for user in userlist:
        username = user.split('$$ ')[0]
        user_ip.update( {username: ip_list.pop()} )
        user_cookie.update( {username: cookie_list.pop()} )

# update dictionary for apps and their users
with open('APIM_scenario/data/app_creation.csv') as file:
    appList = file.read().split('\n')

    for app in appList:
        if app != "":
            appName = app.split('$ ')[0]
            users_apps.update( {appName: []} )

# set ips with username, access tokens and append to relevant lists
with open('APIM_scenario/api_invoke_tokens.csv') as file:
    user_token = csv.reader(file)

    for row in user_token:
        username = row[0]
        app_name = row[1]
        token = row[2]
        ip = user_ip.get(username)
        cookie = user_cookie.get(username)

        (users_apps[app_name]).append([username,token,ip,cookie])

# execute the scenario according to the script

with open('dataset/generated/{}'.format(filename), 'w') as file:
    file.write("timestamp,api,access_token,ip_address,cookie,invoke_path,http_method\n")

with open('APIM_scenario/data/api_invoke_scenario.csv') as file:
    scenario_data = csv.reader(file, delimiter='$')
    req_count = 0

    for row in scenario_data:
        app_name = row[0]
        invokes = row[1]
        invokes = invokes.strip('][').split("],[")
        starttime = datetime.timedelta(minutes=random.randrange(40), seconds=random.randrange(60))

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
                no_of_requests = varySlightly(call_median, user_count) + 10
                simultaneous_requests = random.randrange(no_of_requests)

                # time stamp list
                time_stamps = genTimeList(starttime, no_of_requests-simultaneous_requests+1)

                simultaneous_timestamp = str(time_stamps.pop(0))
                for i in range(simultaneous_requests):
                    final_string = simultaneous_timestamp + "," + api_name + "," + user[1] + "," + user[2] + "," + user[3] + "," + full_path + "," + method + "\n"      # timestamp,api_name,access_token,ip,cookie,path,method

                    with open('dataset/generated/{}'.format(filename), 'a+') as file:
                        file.write(final_string)

                for i in range(no_of_requests-simultaneous_requests):
                    timestamp = str(time_stamps.pop(0))
                    final_string = timestamp + "," + api_name + "," + user[1] + "," + user[2] + "," + user[3] + "," + full_path + "," + method + "\n"      # timestamp,api_name,access_token,ip,cookie,path,method

                    with open('dataset/generated/{}'.format(filename), 'a+') as file:
                        file.write(final_string)


print("[INFO] "+str(dt.now())+" Data generation successful!")
