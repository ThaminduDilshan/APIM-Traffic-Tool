'''
This python script will generate 100 random person data and write them to a file named 'user_generation.csv'. Csv file format is as below.
<username>, <password>, <first_name>, <last_name>, <organization>, <country>, <email>, <no(land)>, <no(mobile)>, <IM>, <url>
delimiter : '$$ '
'''


import rstr
from faker import Faker
import argparse
import os
import yaml

# global variables
faker = Faker()
usernames = []
scenario_name = None
abs_path = os.path.abspath(os.path.dirname(__file__))

with open(abs_path+'/../../../../config/traffic-tool.yaml', 'r') as file:
    traffic_config = yaml.load(file, Loader=yaml.FullLoader)
scenario_name = traffic_config['scenario_name']


# get username and password for a given user (username and password are considered as the same)
def genUnPw(firstname:str, num:int):
    username = firstname.lower() + str(num)
    if len(username) < 5:
        username += '123'
    usernames.append(username)
    return username


# generate random user data
def generateUser(num:int):
    user = []
    firstname = faker.first_name()
    username = genUnPw(firstname, num)
    user.append(username)
    user.append(username)
    user.append(firstname)
    user.append(faker.last_name())
    user.append(faker.company())
    user.append(faker.country())
    user.append(firstname.lower() + str(num) + '@gmail.com')
    user.append(faker.phone_number())
    user.append(faker.phone_number())
    user.append(firstname.lower() + str(num))
    user.append('http://{0}.{1}.com/{2}/?{3}'.format(rstr.domainsafe(), rstr.letters(3), rstr.urlsafe(), rstr.urlsafe()))

    return user


# create app name, username pattern according to the scenario
def app_userScenario():
    finalArr = []
    finalStr = ""
    finalArr.append([ usernames[i]+",Online Shopping\n" for i in range(0,15) ])     # only online shopping app users
    finalArr.append([ usernames[i]+",Taxi\n" for i in range(15,50) ])     # only taxi app users
    finalArr.append([ usernames[i]+",CricScore\n" for i in range(50,60) ])     # only cricscore app users

    finalArr.append([ usernames[i]+",Online Shopping\n" for i in range(60,70) ])  # both shopping and taxi app users
    finalArr.append([ usernames[i]+",Taxi\n" for i in range(60,70) ])

    finalArr.append([ usernames[i]+",Online Shopping\n" for i in range(70,75) ])  # both shopping and cricscore app users
    finalArr.append([ usernames[i]+",CricScore\n" for i in range(70,75) ])

    finalArr.append([ usernames[i]+",Taxi\n" for i in range(75,90) ])  # both taxi and cricscore app users
    finalArr.append([ usernames[i]+",CricScore\n" for i in range(75,90) ])

    finalArr.append([ usernames[i]+",Online Shopping\n" for i in range(90,100) ])  # all 3 app users
    finalArr.append([ usernames[i]+",Taxi\n" for i in range(90,100) ])
    finalArr.append([ usernames[i]+",CricScore\n" for i in range(90,100) ])

    for outer in finalArr:
        for inner in outer:
            finalStr += inner

    file = open(abs_path+'/../../data/scenario/{}/data/user_app_pattern.csv'.format(scenario_name), 'w')
    file.write(finalStr)
    file.close()

    print('User app pattern generation successful!')


# generate 100 users and write data to a csv file ('$$ ' is used as delimiter)
def genUsersCSV():
    csvString = ""
    for i in range(100):
        userArr = generateUser(i+1)
        for ele in userArr:
            csvString += ele + '$$ '
        csvString += '\n'

    file = open(abs_path+'/../../data/scenario/{}/data/user_generation.csv'.format(scenario_name), 'w')
    file.write(csvString)
    file.close()
    print('User generation successful!')


# execute
parser = argparse.ArgumentParser("generate user details")
parser.add_argument("option", help="Pass 0 to generate only user details. Pass 1 to generate user details and the scenario distribution", type=int)
args = parser.parse_args()

if args.option == 0:
    genUsersCSV()
elif args.option == 1:
    genUsersCSV()
    app_userScenario()
else:
    print("Invalid argument value {}!".format(args.option))
