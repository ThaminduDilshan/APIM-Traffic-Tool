import csv
import random
import string
from faker import Factory
import datetime


# Variables
filename = "api_invoke_1.csv"
user_ip = {}
user_cookie = {}
users_shopping = []
users_taxi = []
users_cricscore = []
# final_string = "access_token,ip_address,cookie\n"
fake_generator = Factory.create()


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
    This method will pop and return an user from the relevant user list
'''
def getUser(app_name):
    user = None
    if app_name == "Online Shopping":
        user = users_shopping.pop()
    elif app_name == "Taxi":
        user = users_taxi.pop()
    elif app_name == "CricScore":
        user = users_cricscore.pop()

    return user


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
with open('data/user_generation.csv') as file:
    userlist = file.read().split('\n')

    ip_list = genUniqueIPList(len(userlist))
    cookie_list = genUniqueCookieList(len(userlist))

    for user in userlist:
        username = user.split('$$ ')[0]
        user_ip.update( {username: ip_list.pop()} )
        user_cookie.update( {username: cookie_list.pop()} )

# set ips with username, access tokens and append to relevant lists
with open('api_invoke_tokens.csv') as file:
    user_token = csv.reader(file)

    for row in user_token:
        username = row[0]
        app_name = row[1]
        token = row[2]
        ip = user_ip.get(username)
        cookie = user_cookie.get(username)

        if app_name == "Online Shopping":
            users_shopping.append([username,token,ip,cookie])
        elif app_name == "Taxi":
            users_taxi.append([username,token,ip,cookie])
        elif app_name == "CricScore":
            users_cricscore.append([username,token,ip,cookie])

# execute the scenario according to the script
with open('dataset/generated/{}'.format(filename), 'w') as file:
    file.write("timestamp,api,access_token,ip_address,cookie\n")

with open('data/api_invoke_scenario.csv') as file:
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
            users.append(getUser(app_name))

        for invoke in invokes:
            row2 = invoke.split(',')
            api_name = row2[1]
            method = row2[2]
            call_median = int(row2[3])
            path = row2[4]

            for user in users:
                no_of_requests = varySlightly(call_median, user_count)

                # time stamp list
                time_stamps = genTimeList(starttime, no_of_requests)

                for i in range(no_of_requests):     # access_token,ip,cookie
                    timestamp = str(time_stamps.pop(0))
                    final_string = timestamp + "," + api_name + "," + user[1] + "," + user[2] + "," + user[3] + "\n"      # api_name,access_token,ip,cookie,timestamp

                    with open('dataset/generated/{}'.format(filename), 'a+') as file:
                        file.write(final_string)

# # write final output
# with open('dataset/{}'.format(filename), 'w') as file:
#     file.write(final_string)

print("Data generation successful!")
