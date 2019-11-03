import csv
import random
import string
import datetime
from datetime import datetime as dt
from faker import Factory
import argparse
import pickle
import yaml


parser = argparse.ArgumentParser("generate traffic data")
parser.add_argument("filename", help="Enter a filename to write final output", type=str)
args = parser.parse_args()
filename = args.filename + ".csv"

# Variables
no_of_data_points = None
script_starttime = None
scenario_pool = []
current_data_points = 0

fake_generator = Factory.create()


'''
    This method will load and set the configuration data
'''
def loadConfig():
    global no_of_data_points

    with open('../../../../config/traffic-tool.yaml', 'r') as file:
        traffic_config = yaml.load(file, Loader=yaml.FullLoader)

    no_of_data_points = int(traffic_config['tool-config']['no-of-data-points'])


'''
    This method will write the given log output to the log.txt file
'''
def log(tag, write_string):
    with open('../../../../logs/traffic-tool.log', 'a+') as file:
        file.write("[{}] ".format(tag) + str(dt.now()) + ": " + write_string + "\n")


'''
    This method will generate a random time stamp list for a given number of invokes
'''
def genTimeList(starttime, no_of_invokes:int):
    timestamps = []
    current = starttime
    for i in range(no_of_invokes):
        current += datetime.timedelta(minutes=random.randrange(int(55/no_of_invokes)+5), seconds=random.randrange(40))
        timestamps.append(current)

    return timestamps


'''
    This method will write the invoke request data to a file
'''
def writeInvokeData(timestamp, api_name, api_version, path, access_token, method, user_ip, cookie, app_name, username):
    code = '200'
    write_string = str(timestamp) + "," + api_name + "," + access_token + "," + user_ip + "," + cookie + "," + api_name+"/"+api_version+"/"+path + "," + method + "," + str(code) + "\n"

    with open('../../../../dataset/generated-traffic/{}'.format(filename), 'a+') as file:
        file.write(write_string)


'''
    This method will take a given invoke scenario and generate data for it
'''
def genInvokeData(starttime, scenario_row):
    global no_of_data_points, current_data_points

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

    # time stamps
    simultaneous_requests = random.randint(0, no_of_requests)
    time_stamps = genTimeList(starttime, no_of_requests-simultaneous_requests+1)
    simultaneous_timestamp = str(time_stamps.pop(0))

    # simulate scenario
    for i in range(simultaneous_requests):
        writeInvokeData(simultaneous_timestamp, api_name, api_version, path, access_token, method, user_ip, cookie, app_name, username)
        current_data_points += 1
        if current_data_points >= no_of_data_points:
            return True

    for i in range(no_of_requests-simultaneous_requests):
        timestamp = str(time_stamps.pop(0))
        writeInvokeData(timestamp, api_name, api_version, path, access_token, method, user_ip, cookie, app_name, username)
        current_data_points += 1
        if current_data_points >= no_of_data_points:
            return True


'''
    Generate the dataset according to the scenario
    Usage: python3 gen_invoke_data.py filename
    output folder: dataset/generated-traffic/
'''

loadConfig()

with open('../../../../dataset/generated-traffic/{}'.format(filename), 'w') as file:
    file.write("timestamp,api,access_token,ip_address,cookie,invoke_path,http_method,response_code\n")

scenario_pool = pickle.load(open("../../data/pickle/user_scenario_pool.sav", "rb"))
script_starttime = dt.now()

print("[INFO] Scenario loaded successfully. Wait until data generation complete!")
log("INFO", "Scenario loaded successfully. Wait until data generation complete!")

# execute the scenario and generate the dataset
ret_val = None

while True:
    if ret_val:
        break

    # shuffle the pool
    random.shuffle(scenario_pool)

    for row in scenario_pool:
        starttime = datetime.timedelta(minutes=random.randrange(40), seconds=random.randrange(60))
        ret_val = genInvokeData(starttime, row)
        if ret_val:
            break

time_elapsed = dt.now() - script_starttime
print("[INFO] Data generated successfully. Time elapsed: {} seconds".format(time_elapsed.seconds))
log("INFO", "Data generated successfully. Time elapsed: {} seconds".format(time_elapsed.seconds))
