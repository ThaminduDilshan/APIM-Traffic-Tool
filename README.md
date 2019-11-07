# Introduction

## What is WSO2 API Manager?

WSO2 API Manager is a full lifecycle API Management solution which has an API Gateway and a Microgateway. See more on https://wso2.com/api-management/

## What is APIM Traffic Tool?
APIM Traffic Tool allows you to simulate a real world traffic on WSO2 API Manager. This tool is not just a simple request sender, but it also allows you to setup a user scenario in WSO2 API Manager and generate a set of tokens to invoke APIs. Tool is consisting of two main components traffic tool and attack tool. Trafic tool will simulate a real world traffic pattern while attack tool will simulate a given attack on WSO2 API Manager. APIM Traffic Tool can also be used to generate an API invoking traffic dataset and attack dataset for Machine Learning purposes.

## How does APIM Traffic Tool Works?
Tool will allow user to create a set of APIs and Applications in WSO2 API Manager according to a given scenario. Also the tool will signup a set of users in WSO2 carbon and set them with subscriber privileges. These user details are generated randomly by the tool. The users should be distributed among applications according to a scenario and traffic tool will generate access tokens for each user-application combination using the password grant type ([see more](https://docs.wso2.com/display/AM260/Password+Grant)).

The traffic tool will continuously send traffic to the WSO2 API Manager throughout a user specified time according to the given pattern.

<attack tool will ...>

# Quick Start Guide

## Prerequisites
1. Install Java 7 or 8 (https://www.oracle.com/technetwork/java/javase/downloads/index.html).

1. Download and install WSO2 API Manager version 2.6.0 (https://wso2.com/api-management/).

1. Install Python 3.6 or higher.

1. Install pip version 3 if not already installed.

1. Install required python packages by running the following command in the project home directory.
   - `$ sudo pip install -r requirement.txt`

1. Download and install Apache jmeter version 5.1.1 or higher (http://jmeter.apache.org/download_jmeter.cgi).

1. Add following two packages to the `<JMETER_HOME>/lib` folder.
   - Download and add apache ivy (https://ant.apache.org/ivy/download.cgi)
   - Add attack tool helper package (can be found from `<TOOL_HOME>/resources/jars/attack-tool-helpers.jar`)

1. Verify that all configurations are set for the traffic and attack scripts.

## Configuring the Tool
Default configurations for WSO2 API Manager and default scenario are given in all the config files. If you are running WSO2 API Manager on different configurations or using the tool for a custom scenario, you can change the tool configurations as stated below. All configuration files are in the `<TOOL_HOME>/config` folder.

1. Add your jmeter path in the `<TOOL_HOME>/config/user-settings.yaml` file.

1. Enter correct API Manager version (please state as `2.6` or `3.0`), endpoints, protocol type, host ip and ports of WSO2 API Manager in the `<TOOL_HOME>/config/apim.yaml` file (Default ports and details can be found at https://docs.wso2.com/display/AM260/Default+Product+Ports).

   ```
   Endpoints for WSO2 API Manager 2.6.0

   token_registration_endpoint: /client-registration/v0.14/register
   token_endpoint: /token
   publisher_api: /api/am/publisher/v0.14/apis
   store_application: /api/am/store/v0.14/applications
   store_subscription: /api/am/store/v0.14/subscriptions
   user_signup: /store/site/blocks/user/sign-up/ajax/user-add.jag
   delete_user: /services/RemoteUserStoreManagerService.RemoteUserStoreManagerServiceHttpsSoap11Endpoint

   Endpoints for WSO2 API Manager 3.0.0

   token_registration_endpoint: /client-registration/v0.15/register
   token_endpoint: /token
   publisher_api: /api/am/publisher/v0.15/apis
   store_application: /api/am/store/v0.15/applications
   store_subscription: /api/am/store/v0.15/subscriptions
   user_signup: /api/identity/user/v1.0/me
   delete_user: /services/RemoteUserStoreManagerService.RemoteUserStoreManagerServiceHttpsSoap11Endpoint
   ```

1. Add details of each API (name, context, version, resources) under apis section in `<TOOL_HOME>/config/apim.yaml` file.

   ```
   Example Usage

   apis:
    - name: news
      context: news
      version: 1
      resources:
       - method: GET
         path: menu

    - name: places
      context: places
      version: 1
      resources:
        - method: GET
          path: menu
   ```

1. Configure the `<TOOL_HOME>/config/traffic-tool.yaml` file as stated below (Configurations for the traffic script).
   - Enter throttling tier, api visibility, production and sandbox endpoints for the APIs under api section (APIs are created using these configurations).
   - Enter payload to send with POST requests when simulating a normal traffic under api section.
   - Enter throttling tier and token validity period for the applications under application section (Applications are created using these configurations).
   - Enter correct subscription tier for the app api subscriptions.
   - Enter scenario name in front of scenario_name section. If you are using the default scenario, scenario_name is `scenario_example`.
   - Enter protocol type, ip address and port of an hosted API under api_host section.
   - Configure tool_config section as to the following definitions.
      - `no_of_processes`: No of processes to be used for the API invoking
      - `max_connection_refuse_count`: Maximum number of connection refuse count allowed. Traffic tool will stop after the given number of connection refuses.
      - `no_of_data_points`: No of data points or requests to be generated when generating the traffic data without invoking.
      - `heavy_traffic`: If you want to simulate a heavy traffic, set this value as `true`. Otherwise set it to `false`.

1. Configure the `<TOOL_HOME>/config/attack-tool.yaml` file as stated below (Configurations for the attack script).
   - <attack tool configs>

## Using the Traffic Tool
To use the traffic tool run the following command with the desired argument in a command line inside the `<TOOL_HOME>/bin` folder. To list down available options and their command line arguments, just run the command with the flag -h.

`$ ./traffic-tool.sh argument_number`

```
$ ./traffic-tool.sh -h
Traffic Tool Options
1: Generate data for example scenario
2: Create scenario in APIM
3: Generate access tokens
4: Generate traffic data (without invoking)
5: Simulate traffic
all: Setup scenario and simulate traffic
stop: Stop traffic tool
clean: Cleanup scenario data in API Manager
```

#### 1. Generate Random User Details with Example Scenario Distribution
Traffic tool allows you to generate a set of random user details and distribute them among applications according to the example scenario in just a single step. Simply run the shell script with the argument 1.

`$ ./traffic-tool.sh 1`

#### 2. Create Example Scenario in WSO2 API Manager
Traffic tool is capable of creating APIs, applications, subscribe them and signup a set of users in WSO2 API Manager according to the given scenario. Simply run the shell script with the argument 2.

```
$ ./traffic-tool.sh 2
```

Please make sure you don't have any errors in the shell (Error count should be zero). If you encountered with errors, it is recommended to run the `clean` command and rerun the above command.
```
Waiting for possible Shutdown/StopTestNow/HeapDump/ThreadDump message on port 4445
summary +      5 in 00:00:04 =    1.2/s Avg:   620 Min:    31 Max:  1150 Err:     0 (0.00%) Active: 1 Started: 2 Finished: 1
summary +     32 in 00:00:31 =    1.0/s Avg:   142 Min:    11 Max:   671 Err:     0 (0.00%) Active: 1 Started: 4 Finished: 3
summary =     37 in 00:00:35 =    1.1/s Avg:   207 Min:    11 Max:  1150 Err:     0 (0.00%)
summary +     15 in 00:00:30 =    0.5/s Avg:    19 Min:     7 Max:    29 Err:     0 (0.00%) Active: 1 Started: 4 Finished: 3
summary =     52 in 00:01:05 =    0.8/s Avg:   153 Min:     7 Max:  1150 Err:     0 (0.00%)
summary +    112 in 00:00:21 =    5.4/s Avg:   147 Min:     4 Max:   593 Err:     0 (0.00%) Active: 0 Started: 6 Finished: 6
summary =    164 in 00:01:26 =    1.9/s Avg:   149 Min:     4 Max:  1150 Err:     0 (0.00%)
Tidying up ...    @ Wed Nov 06 11:04:22 IST 2019 (1573018462316)
... end of run
```

#### 3. Generate Access Tokens
API consumers require access tokens in order to access resources. Run the shell script with the argument 3 to generate a set of access tokens for all user-application combinations. Tokens will be saved in scenario/<scenario_name>/api_invoke_tokens.csv file with ‘,’ as the delimiter.

```
$ ./traffic-tool.sh 3
```

#### 4. Generate the Traffic Dataset without Invoking
Traffic tool will allow you to generate an API invoking traffic without actually invoking the APIs. Run the shell script with the argument 4. You will be prompted for a filename. Enter the filename without a file extension(without .txt, .csv, etc) and the output or the dataset will be saved in dataset/generated-traffic/<filename>.csv directory.

```
$ ./traffic-tool.sh 4
Enter filename (without file extension):
gen_traffic_data
```

#### 5. Simulate a Traffic on API Manager
To simulate an API invoking traffic on WSO2 API Manager, run the shell script with the argument 5. You will be prompted for a filename and the script run time. Enter the filename without a file extension(without .txt, .csv, etc) and the output or the dataset will be saved in dataset/traffic/<filename>.csv directory. Traffic will be executed throughout the given time (Enter the time in minutes when prompted).

```
$ ./traffic-tool.sh 5
Enter filename (without file extension):
output
Enter script execution time in minutes:
15
```

#### 6. Setup Scenario and Simulate a Traffic
APIM Traffic Tool allows you to simply run the steps 1,2,3 and 5 from a single command. Just run the shell script with the argument 'all'.

```
$ ./traffic-tool.sh all
Enter filename (without file extension):
output
Enter script execution time in minutes:
15
```

#### 7. Stop the Traffic Tool
To stop the API invoking or data generation while the script is running, run the shell script with the argument 'stop'.

`$ ./traffic-tool.sh stop`

#### 8. Remove Scenario from API Manager
After simulating a traffic you may want to remove all the created APIs, applications and users from the API Manager. Run the shell script with the argument 'clean'.

`$ ./traffic-tool.sh clean`

You have to run the steps 1,2,3 and 5 inorder to simulate an API invoking traffic according to the example scenario. If you are simulating for a custom scenario, only run steps 2,3 and 5 after following the given steps under the heading “Adding Custom APIM Scenario”. You can also generate the traffic dataset without actually invoking the API Manager using the step 4 instead of step 5.

## Using the Attack Tool
To use the attack tool run the following command with the desired argument in a command line inside the `<TOOL_HOME>/bin` folder. To list down available options and their command line arguments, just run the command with the flag -h.

<attack tool commands>

# Additional Details

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
Adding a custom API Manager scenario is little bit tricky task. As for the current version of the APIM Traffic Tool, you have to configure a set of files in order to invoke for a custom scenario. First you have to think and design a real world API access pattern which is similar to the example scenario given. Then follow below steps to change scenario data files. Default scenario files are at `<TOOL_HOME>/lib/traffic-tool/data/scenario/scenario_example/data/` directory. You can add a new folder named as your scenario_name to the `/scenario` folder and add a `/data` folder containing following files. Line seperator for all csv files is the new line character ('\n').

1. api_creation.csv
Enter details of APIs (API name, description, context and a tag). Delimiter for csv is the comma(',').

1. api_creation_swagger.csv
Provide swagger definitions of all the APIs seperated by new line character ('\n').

1. app_creation.csv
Enter details of applications (Application name and description). Delimiter for csv is the dollar sign and a space('$<space>').

1. app_api_subscription_admin.csv
Enter all application-api combinations which the subscriptions should happen. Give application name and API name seperated by a comma (',').

1. api_invoke_scenario.csv
This file should be prepared according to your invoke scenario. Each row is for a different user type in the scenario table. A row in the file is in the following format. '$' sign is used as the delimiter. You can add any number of patterns to the list in the format `[no_of_users,http_method,no_of_requests,resource_path]`.

   `<application_name>$[[pattern_1],[pattern_2]]`

1. user_generation.csv
This file contains the user details in the following format. Delimiter for csv is two dollar signs and a space ($$<space>).

   `<username>, <password>, <first_name>, <last_name>, <organization>, <country>, <email>, <no(land)>, <no(mobile)>, <IM>, <url>`

   This file can be generated for 100 random users by running the following command.

   `$ ./traffic-tool.sh user_details`

1. user_app_pattern.csv
Above generated users should be distributed among applications inorder to generate access tokens. This file contains all username-application_name combinations seperated by a new line character ('\n'). Csv delimiter is the comma (',').
