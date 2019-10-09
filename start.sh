#!/bin/sh

func_help() {
  echo "\nTraffic Tool Options"
  echo "1. To generate user details\t\t\t: gen_user_details"
  echo "2. To create scenario in WSO2 APIM\t\t: create_scenario"
  echo "3. To generate access tokens\t\t\t: gen_tokens"
  echo "4. To generate traffic data (without invoking)\t: gen_invoke_data"
  echo "5. To simulate a traffic\t\t\t: traffic"
}

func_gen_user_details() {
  # run apim_scenario_GEN_userdetails.py with arg: 0
}

func_create_scenario() {
  # check if these files exists-> $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
  # if not-> error
  # run API Scenario - multiple end users.jmx
}

func_gen_tokens() {
  # check if these files exists-> $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
  # if not-> error
  # remove these existing files-> $$$$$$$$$$$$$$$$$$$$$$$$$$$$$
  # run Generate token list.jmx
}

func_gen_invoke_data() {
  # check if these files exists-> $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
  # if not-> error
  # remove these existing files-> $$$$$$$$$$$$$$$$$$$$$$$$$$$$$
  # run generate_invokeData.py
}

func_traffic() {
  # check if these files exists-> $$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$$
  # if not-> error
  # remove these existing files-> $$$$$$$$$$$$$$$$$$$$$$$$$$$$$
  # run invoke_API.py
}


case "$1" in
  -h)
    func_help
    exit 0
  ;;
  gen_user_details)
    func_gen_user_details | tee -a logs/shell-logs.log
    exit 0
  ;;
  create_scenario)
    func_create_scenario | tee -a logs/shell-logs.log
    exit 0
  ;;
  gen_tokens)
    func_gen_tokens | tee -a logs/shell-logs.log
    exit 0
  ;;
  gen_invoke_data)
    func_gen_invoke_data | tee -a logs/shell-logs.log
    exit 0
  ;;
  traffic)
    func_traffic | tee -a logs/shell-logs.log
    exit 0
  ;;
  *)
    echo "Invalid argument!"
    func_help
    exit 1
  ;;
esac







# echo "Do you want to create the scenario in WSO2 API Manager [Yes/No]?"
# read response1
#
# if ["$response1" == "Yes"] || ["$response1" == "yes"] || ["$response1" == "Y"] || ["$response1" == "y"]
# then
#   #
# elif ["$response1" == "No"] || ["$response1" == "no"] || ["$response1" == "N"] || ["$response1" == "n"]
# then
#   #
# else
#   #
# fi
#
#
#
# run_script() {
#   echo "Make sure WSO2 API Manager running on default ports. Do you want to continue [Yes/No]?"
#   read response2
# }
#
#
# echo "What is your name?"
# read PERSON
# echo "Hello, $PERSON"
