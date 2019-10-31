#!/bin/sh

#JMPATH="/home/thamindu/Documents/Applications/apache-jmeter-5.1.1/bin"

func_help() {
  echo "Traffic Tool Options"
  echo "1: To generate user details"
  echo "2: To generate user details and the example scenario"
  echo "3: To create scenario in WSO2 APIM"
  echo "4: To generate access tokens"
  echo "5: To generate traffic data (without invoking)"
  echo "6: To simulate a traffic"
  echo "7: To stop the traffic tool"
}

func_gen_user_details() {
  if command -v python3 &>/dev/null; then
    python3 apim_scenario_GEN_userdetails.py 0
  else
    echo "Python 3 is required for the command!"
    exit 1
  fi
}

func_gen_example_scenario() {
  if command -v python3 &>/dev/null; then
    python3 apim_scenario_GEN_userdetails.py 1
  else
    echo "Python 3 is required for the command!"
    exit 1
  fi
}

func_create_scenario() {
  if [ -e "$(pwd)"/APIM_scenario/data/api_creation.csv -a -e "$(pwd)"/APIM_scenario/data/api_creation_swagger.csv -a -e "$(pwd)"/APIM_scenario/data/app_creation.csv -a -e "$(pwd)"/APIM_scenario/data/app_api_subscription_admin.csv -a -e "$(pwd)"/APIM_scenario/data/user_generation.csv ];
  then
    rm -f APIM_scenario/api_invoke_keySecret-multipleEndUsers.csv
    echo "Enter your jmeter path (Ex:- /home/user/Documents/apache-jmeter-5.1.1/bin)"
    read JMPATH
    $JMPATH/jmeter -n -t 'API Scenario - multiple end users.jmx' -l logs/jmeter-results.log -j logs/jmeter.log
  else
    echo "Missing one or more required files in the 'APIM_scenario/data' directory"
    exit 1
  fi
}

func_gen_tokens() {
  if [ -e "$(pwd)"/APIM_scenario/data/app_creation.csv -a -e "$(pwd)"/APIM_scenario/data/user_app_pattern.csv ];
  then
    rm -f APIM_scenario/api_invoke_tokens.csv
    echo "Enter your jmeter path (Ex:- /home/user/Documents/apache-jmeter-5.1.1/bin)"
    read JMPATH
    $JMPATH/jmeter -n -t 'Generate token list.jmx' -l logs/jmeter-results.log -j logs/jmeter.log
  else
    echo "Missing one or more required files in the 'APIM_scenario/data' directory"
    exit 1
  fi
}

func_gen_invoke_data() {
  if [ -e "$(pwd)"/APIM_scenario/data/user_generation.csv -a -e "$(pwd)"/APIM_scenario/data/app_creation.csv -a -e "$(pwd)"/APIM_scenario/api_invoke_tokens.csv -a -e "$(pwd)"/APIM_scenario/data/api_invoke_scenario.csv ];
  then
    echo "Enter filename (without file extension):"
    read FILENAME
    # python3 generate_invokeData.py $FILENAME
    #chmod +x generate_invokeData.py
    nohup python3 generate_invokeData.py $FILENAME >> logs/shell-logs.log &
  else
    echo "Missing one or more required files in the 'APIM_scenario/data' directory"
    exit 1
  fi
}

func_traffic() {
  if [ -e "$(pwd)"/APIM_scenario/data/user_generation.csv -a -e "$(pwd)"/APIM_scenario/data/app_creation.csv -a -e "$(pwd)"/APIM_scenario/api_invoke_tokens.csv -a -e "$(pwd)"/APIM_scenario/data/api_invoke_scenario.csv ];
  then
    echo "Enter filename (without file extension): "
    read FILENAME
    echo "Enter script execution time in minutes: "
    read EXECTIME
    # python3 invoke_API.py $FILENAME
    chmod +x invoke_API.py
    nohup python3 invoke_API.py $FILENAME $EXECTIME >> logs/shell-logs.log &
    echo $! > data/invoke_API.pid
  else
    echo "Missing one or more required files in the 'APIM_scenario/data' directory"
    exit 1
  fi
}

func_stop_traffic() {
  PID=`cat data/invoke_API.pid 2>/dev/null`
  if [ -z $PID ]
  then
    echo "Traffic Tool is Not Running"
  else
    kill -0 $PID 2>/dev/null
    if [ $? -eq 0 ]
    then
      kill -9 $PID
      if [ $? -eq 0 ]
      then
          echo "Traffic Tool Stopped Successfully"
      fi
    else
      echo "Traffic Tool Already Stopped"
    fi
  fi
  > data/invoke_API.pid
}


case "$1" in
  -h)
    func_help
    exit 0
  ;;
  1)
    func_gen_user_details | tee -a logs/shell-logs.log
    exit 0
  ;;
  2)
    func_gen_example_scenario | tee -a logs/shell-logs.log
    exit 0
  ;;
  3)
    func_create_scenario | tee -a logs/shell-logs.log
    exit 0
  ;;
  4)
    func_gen_tokens | tee -a logs/shell-logs.log
    exit 0
  ;;
  5)
    func_gen_invoke_data | tee -a logs/shell-logs.log
    exit 0
  ;;
  6)
    func_traffic | tee -a logs/shell-logs.log
    exit 0
  ;;
  7)
    func_stop_traffic | tee -a logs/shell-logs.log
    exit 0
  ;;
  *)
    echo "Invalid argument!"
    func_help
    exit 1
  ;;
esac
