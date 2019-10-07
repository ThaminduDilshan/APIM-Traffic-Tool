import csv
import random
import string
import requests
import time
from faker import Factory


# Variables
filename = "api_invoke_1.csv"
user_ip = {}
user_cookie = {}
users_shopping = []
users_taxi = []
users_cricscore = []
# final_string = "access_token,ip_address,cookie\n"
# final_response = "code,text\n"
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
    with open('dataset/ip_list_{}'.format(filename), 'w') as file:
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
    This method will send http requests to the given address: GET, POST only
'''
def sendRequest(url_ip, url_port, api_name, api_version, path, access_token, method, user_ip, cookie):
    url = "https://{}:{}/{}/{}/{}".format(url_ip, url_port, api_name, api_version, path)
    headers = {
        'accept': 'application/json',
        'Authorization': 'Bearer {}'.format(access_token),
        'client-ip': '{}'.format(user_ip),
        'x-forwarded-for': '{}'.format(user_ip),
        'cookie': '{}'.format(cookie)
    }
    code = None
    res_txt = ""

    if method=="GET":
        response = requests.get(url=url, headers=headers, verify=False)
        code = response.status_code
        res_txt = response.text
        # print('code: ', code, ' | ', 'response: ', response.text)
    elif method=="POST":
        data = {"Payload": "sample"}
        response = requests.post(url=url, headers=headers, data=data, verify=False)
        code = response.status_code
        res_txt = response.text
        # print('code: ', code, ' | ', 'response: ', response.text)
    else:
        code = '400'
        res_txt = 'Invalid type!'
        # print('[ERROR] Invalid Type!')

    return code,res_txt



'''
    Execute the scenario and generate the dataset
    Usage: python3 generate_invokeData.py
    output folder: dataset/
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
with open('dataset/{}'.format(filename), 'w') as file:
    file.write("api,access_token,ip_address,cookie\n")

with open('data/api_invoke_scenario.csv') as file:
    scenario_data = csv.reader(file, delimiter='$')
    req_count = 0

    for row in scenario_data:
        app_name = row[0]
        invokes = row[1]
        invokes = invokes.strip('][').split("],[")

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

            for user in users:              # user[username,token,ip,cookie]
                print("Invoking ", user[0], " ...")

                no_of_requests = varySlightly(call_median, user_count)
                for i in range(no_of_requests):
                    final_string = api_name + "," + user[1] + "," + user[2] + "," + user[3] + "\n"      # api_name,access_token,ip,cookie,timestamp

                    # send request
                    # print("started : ", req_count)
                    # res_code, res_txt = sendRequest("10.100.4.187", "8243", api_name, "v1.0.0", path, user[1], method, user[2], user[3])
                    res_code, res_txt = sendRequest("10.100.4.187", "8243", api_name, "1", path, user[1], method, user[2], user[3])
                    req_count += 1
                    # print("Request No: {}   |   Response: {} | {}".format(req_count, res_code, res_txt))
                    final_response = str(res_code) + "," + res_txt + "," + app_name + "," + api_name + "," + user[0] + "," + user[1] + "\n"

                    with open('dataset/{}'.format(filename), 'a+') as file:
                        file.write(final_string)

                    with open('response/res_{}'.format(filename), 'a+') as file:
                        file.write(final_response)

                    # if res_code != 200:
                    #     time.sleep(1)
                    time.sleep(0.01)


# # write final output
# with open('dataset/{}'.format(filename), 'w') as file:
#     file.write(final_string)

# with open('response/res_{}'.format(filename), 'w') as file:
#     file.write(final_response)

print("Data generation successful!")
