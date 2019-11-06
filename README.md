# Introduction

## What is WSO2 API Manager?

WSO2 API Manager is a full lifecycle API Management solution which has an API Gateway and a Microgateway. See more on https://wso2.com/api-management/

## What is APIM Traffic Tool?
APIM Traffic Tool allows you to simulate a real world traffic on WSO2 API Manager. This tool is not just a simple request sender, but it also allows you to setup a user scenario in WSO2 API Manager and generate a set of tokens to invoke APIs. Tool is consisting of two main components traffic tool and attack tool. Trafic tool will simulate a real world traffic pattern while attack tool will simulate a given attack on WSO2 API Manager. APIM Traffic Tool can also be used to generate an API invoking traffic dataset and attack dataset for Machine Learning purposes.

## How does Traffic Tool works?
Tool will allow user to create a set of APIs and Applications in WSO2 API Manager according to a given scenario. Also the tool will signup a set of users in WSO2 carbon and set them with subscriber privileges. These user details are generated randomly by the tool. The users should be distributed among applications according to a scenario and traffic tool will generate access tokens for each user-application combination using the password grant type ([see more](https://docs.wso2.com/display/AM260/Password+Grant)). Then the tool will continuously send traffic to the WSO2 API Manager throughout a user specified time according to the given pattern.

# Quick Start Guide

## Prerequisites
1. Install Java 7 or 8 (https://www.oracle.com/technetwork/java/javase/downloads/index.html).

1. Download and install WSO2 API Manager version 2.6.0 (https://wso2.com/api-management/).

1. Install Python 3.6 or higher.

1. Install pip version 3 if not already installed.

1. Install required python packages by running the following command in the project home directory.
   - `$ pip install -r requirement.txt`

1. Download and install Apache jmeter version 5.1.1 or higher (http://jmeter.apache.org/download_jmeter.cgi).

1. Add following two packages to the `<JMETER_HOME>/lib` folder.
   - Download and add apache ivy (https://ant.apache.org/ivy/download.cgi)
   - Add attack tool helper package (can be found from `<TOOL_HOME>/resources/jars/attack-tool-helpers.jar`)

1. Verify that all configurations are set for the traffic and attack scripts.

## Configuring the Tool
Default configurations for WSO2 API Manager and default scenario are given in all the config files. If you are running WSO2 API Manager on different configurations or using the tool for a custom scenario, you can change the tool configurations as stated below. All configuration files are in the `<TOOL_HOME>/config` folder.

1. Enter correct protocol type, host ip and ports of WSO2 API Manager in the `<TOOL_HOME>/config/apim.yaml` file (Default ports and details can be found at https://docs.wso2.com/display/AM260/Default+Product+Ports).

1. Add details of each API (name, context, version, resources) under apis section in `<TOOL_HOME>/config/apim.yaml` file.

1. Configure the `<TOOL_HOME>/config/traffic-tool.yaml` file as stated below (Configurations for the traffic script).
   - Enter throttling tier, api visibility, production and sandbox endpoints for the APIs under api section (APIs are created using these configurations).
   - Enter payload to send with POST requests when simulating a normal traffic under api section.
   - Enter throttling tier and token validity period for the applications under application section (Applications are created using these configurations).
   - Enter correct subscription tier for the app api subscriptions.
   - Enter scenario name in front of scenario_name section. If you are using the default scenario, scenario_name is 'scenario_example'.
   - Enter protocol type, ip address and port of an hosted API under api_host section.
   - Configure tool_config section as to the following definitions.
      - no_of_processes: No of processes to be used for the API invoking
      - max_connection_refuse_count: Maximum number of connection refuse count allowed. Traffic tool will stop after the given number of connection refuses.
      - no_of_data_points: No of data points or requests to be generated when generating the traffic data without invoking.
      - heavy_traffic: If you want to simulate a heavy traffic, set this value as `true`. Otherwise set it to `false`.

1. Configure the `<TOOL_HOME>/config/attack-tool.yaml` file as stated below (Configurations for the attack script).
   - $$

## Using the Traffic Tool
To use the traffic tool run the following command with the desired argument in a command line inside the `<TOOL_HOME>/bin` folder. To list down available options and their command line arguments, just run the command with the flag -h.

`$ ./start.sh argument_number`

```
$ ./start.sh -h
Traffic Tool Options
1: To generate user details
2: To generate user details and the example scenario
3: To create scenario in WSO2 APIM
4: To generate access tokens
5: To generate traffic data (without invoking)
6: To simulate a traffic
7: To stop the traffic tool
```

#### 1. Generate Random User Details
Traffic tool allows you to generate a set of random user details for the example scenario. Simply run the shell script with the argument 1. All details will be saved in a file named APIM_scenario/data/user_generation.csv with ‘$$’ as the delimiter. Csv file format is as below.
> username, password, first_name, last_name, organization, country, email, no(land), no(mobile), IM, url

`$ ./start.sh 1`

#### 2. Generate Random User Details with Example Scenario Distribution
Traffic tool allows you to generate a set of random user details and distribute them among applications according to the example scenario in just a single step. Simply run the shell script with the argument 2.

`$ ./start.sh 2`

#### 3. Create Example Scenario in WSO2 API Manager
Traffic tool is capable of creating APIs, applications, subscribe them and signup a set of users in WSO2 API Manager according to the given scenario. Simply run the shell script with the argument 3. You will be prompted for the jmeter path. Enter the path of the bin folder.

```
$ ./start.sh 3
Enter your jmeter path (Ex:- /home/user/Documents/apache-jmeter-5.1.1/bin)
/home/user123/Documents/apache-jmeter-5.1.1/bin
```

#### 4. Generate Access Tokens
API consumers require access tokens in order to access resources. Run the shell script with the argument 4 to generate a set of access tokens for all user-application combinations. Tokens will be saved in APIM_scenario/api_invoke_tokens.csv file with ‘,’ as the delimiter. You will be prompted for the jmeter path. Enter the path of the bin folder.

```
$ ./start.sh 4
Enter your jmeter path (Ex:- /home/user/Documents/apache-jmeter-5.1.1/bin)
/home/user123/Documents/apache-jmeter-5.1.1/bin
```

#### 5. Generate the Traffic Dataset without Invoking
##

#### 6. Simulate a APIM Traffic
To simulate an API invoking traffic on WSO2 API Manager, run the shell script with the argument 6. You will be prompted for a filename and the script run time. Enter a filename without a file extension(without .txt, .csv, etc) and the output or the dataset will be saved in dataset/<filename>.csv directory. Traffic will be executed throughout the given time (Enter the time in minutes when prompted).

```
$ ./start.sh 6
Enter filename (without file extension):
output
Enter script execution time in minutes:
15
```

#### 7. Stop the Traffic Tool
To stop the API invoking while the script is running, run the shell script with the argument 7.

`$ ./start.sh 7`


You have to run the steps 2,3,4 and 6 inorder to simulate an API invoking traffic according to the example scenario. If you are simulating for a custom scenario, only run steps 3,4 and 6 after following the given steps under the heading “Adding Custom APIM Scenario”. You can also generate the traffic dataset without actually invoking the API Manager using the step 5 instead of step 6.

## Example Scenario
APIM Traffic Tool ships with an example API invoking scenario. You can simply setup the environment and let the invoking happen in a few simple steps. Below is the example API invoke scenario used in the Traffic Tool.
Scenario is involved with following 6 different APIs and 3 different applications.

##### APIs
* News API - This is an API which users can query by keywords, topics, publications.
* Places API - Users can find popular places like food shops, banks, etc using this API.
* Map API - This is an API providing location data, traffic info, real-time updates, etc
* Weather API - Users can query about whether info in a particular location, country or city.
* Payment API - This is an API to securely perform online and mobile payments.
* Cricket API - This is a cricket API providing live scores, teams, player details, etc.

##### Applications
* Online Shopping App - This is an app allowing users to find places to buy their items, food or anything. A User can search for an item, find places, available quantities and their prices and order items through the app. Users can also do the payment when ordering. Also this app notifies users about recently released items and other recent news updates.

* Taxi App - This is a taxi app like Uber or Pickme where users can book cabs. App allows users to find rides for given destinations, book a ride, track ride info and do payments using credit/ debit cards.

* Cricket Score App - This is a cricket app like Cricbuzz or Espn cric info where users can get updates about cricket matches, teams and players. App provides users with latest cric news updates. Also users can get live notification for ongoing matches.

100 users are distributed among those applications according to the following table and invoking happens as stated in the 5th column.

![APIM Example Scenario](/resources/images/APIM_scenario.png)

## Adding Custom APIM Scenario
Adding a custom API Manager scenario is little bit tricky task. As for the current version of the APIM Traffic Tool, you have to configure a set of files in order to invoke for a custom scenario. First you have to think and design a real world API access pattern which is similar to the example scenario given. Then follow below steps to configure scenario data files.
