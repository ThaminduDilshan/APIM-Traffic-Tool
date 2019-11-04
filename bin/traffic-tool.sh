#!/bin/sh

func_help() {
  echo "Traffic Tool Options"
  echo "1: To generate user details"
  echo "2: To generate user details and the example scenario"
  echo "3: To create scenario in WSO2 APIM"
  echo "4: To generate access tokens"
  echo "5: To generate traffic data (without invoking)"
  echo "6: To simulate a traffic"
  echo "7: To stop the traffic tool"
  echo "all: To setup the scenario and simulate a traffic"
}

func_gen_user_details() {
  if command -v python3 &>/dev/null; then
    python3 ../lib/traffic-tool/src/python/gen_user_details.py 0
  elif command -v python &>/dev/null; then
    python ../lib/traffic-tool/src/python/gen_user_details.py 0
  else
    echo "Python 3 is required for the command!"
    exit 1
  fi
}

func_gen_example_scenario() {
  if command -v python3 &>/dev/null; then
    python3 ../lib/traffic-tool/src/python/gen_user_details.py 1
  elif command -v python &>/dev/null; then
    python ../lib/traffic-tool/src/python/gen_user_details.py 1
  else
    echo "Python 3 is required for the command!"
    exit 1
  fi
}

func_create_scenario() {
  echo "Enter the scenario name (press enter if default):"
  read SCENARIONAME
  if [ -z "$SCENARIONAME" ];
    then
      SCENARIONAME="scenario_example"
  fi
  if [ -e "$(pwd)"/../lib/traffic-tool/data/scenario/$SCENARIONAME/data/api_creation.csv -a -e "$(pwd)"/../lib/traffic-tool/data/scenario/$SCENARIONAME/data/api_creation_swagger.csv -a -e "$(pwd)"/../lib/traffic-tool/data/scenario/$SCENARIONAME/data/app_creation.csv -a -e "$(pwd)"/../lib/traffic-tool/data/scenario/$SCENARIONAME/data/app_api_subscription_admin.csv -a -e "$(pwd)"/../lib/traffic-tool/data/scenario/$SCENARIONAME/data/user_generation.csv ];
  then
    rm -f ../lib/traffic-tool/data/scenario/$SCENARIONAME/api_invoke_key_secret.csv
    echo "Enter your jmeter path (Ex:- /home/user/Documents/apache-jmeter-5.1.1/bin)"
    read JMPATH
    $JMPATH/jmeter -n -t '../lib/traffic-tool/src/jmeter/create_api_scenario.jmx' -l ../logs/jmeter-results.log -j ../logs/jmeter.log
  else
    echo "Missing one or more required files in the 'scenario/$SCENARIONAME/' directory"
    exit 1
  fi
}

func_gen_tokens() {
  echo "Enter the scenario name (press enter if default):"
  read SCENARIONAME
  if [ -z "$SCENARIONAME" ];
    then
      SCENARIONAME="scenario_example"
  fi
  if [ -e "$(pwd)"/../lib/traffic-tool/data/scenario/$SCENARIONAME/data/app_creation.csv -a -e "$(pwd)"/../lib/traffic-tool/data/scenario/$SCENARIONAME/data/user_app_pattern.csv -a -e "$(pwd)"/../lib/traffic-tool/data/scenario/$SCENARIONAME/api_invoke_key_secret.csv ];
  then
    rm -f ../lib/traffic-tool/data/scenario/$SCENARIONAME/api_invoke_tokens.csv
    echo "Enter your jmeter path (Ex:- /home/user/Documents/apache-jmeter-5.1.1/bin)"
    read JMPATH
    $JMPATH/jmeter -n -t '../lib/traffic-tool/src/jmeter/generate_token_list.jmx' -l ../logs/jmeter-results.log -j ../logs/jmeter.log
  else
    echo "Missing one or more required files in the 'scenario/$SCENARIONAME/' directory"
    exit 1
  fi
  if command -v python3 &>/dev/null; then
    python3 ../lib/traffic-tool/src/python/gen_invoke_scenario.py
  elif command -v python &>/dev/null; then
    python ../lib/traffic-tool/src/python/gen_invoke_scenario.py
  else
    echo "Python 3 is required for the command!"
    exit 1
  fi
}

func_gen_invoke_data() {
  if [ -e "$(pwd)"/../lib/traffic-tool/data/pickle/user_scenario_pool.sav ];
  then
    echo "Enter filename (without file extension):"
    read FILENAME
    chmod +x ../lib/traffic-tool/src/python/gen_invoke_data.py

    if command -v python3 &>/dev/null; then
      nohup python3 ../lib/traffic-tool/src/python/gen_invoke_data.py $FILENAME >> ../logs/traffic-shell.log 2>&1 &
      echo $! > ../data/traffic_tool.pid
    elif command -v python &>/dev/null; then
      nohup python ../lib/traffic-tool/src/python/gen_invoke_data.py $FILENAME >> ../logs/traffic-shell.log 2>&1 &
      echo $! > ../data/traffic_tool.pid
    else
      echo "Python 3 is required for the command!"
      exit 1
    fi
  else
    echo "Missing 'user_scenario_pool.sav' file"
    exit 1
  fi
}

func_traffic() {
  if [ -e "$(pwd)"/../lib/traffic-tool/data/pickle/user_scenario_pool.sav ];
  then
    echo "Enter filename (without file extension): "
    read FILENAME
    echo "Enter script execution time in minutes: "
    read EXECTIME
    chmod +x ../lib/traffic-tool/src/python/invoke_API.py

    if command -v python3 &>/dev/null; then
      nohup python3 ../lib/traffic-tool/src/python/invoke_API.py $FILENAME $EXECTIME >> ../logs/traffic-shell.log 2>&1 &
      echo $! > ../data/traffic_tool.pid
    elif command -v python &>/dev/null; then
      nohup python ../lib/traffic-tool/src/python/invoke_API.py $FILENAME $EXECTIME >> ../logs/traffic-shell.log 2>&1 &
      echo $! > ../data/traffic_tool.pid
    else
      echo "Python 3 is required for the command!"
      exit 1
    fi
  else
    echo "Missing 'user_scenario_pool.sav' file"
    exit 1
  fi
}

func_stop_traffic() {
  PID=`cat ../data/traffic_tool.pid 2>/dev/null`
  if [ -z $PID ];
  then
    echo "Traffic Tool is Not Running"
  else
    kill -0 $PID 2>/dev/null
    if [ $? -eq 0 ];
    then
      kill -9 $PID
      if [ $? -eq 0 ];
      then
          echo "Traffic Tool Stopped Successfully"
      fi
    else
      echo "Traffic Tool Already Stopped"
    fi
  fi > ../data/traffic_tool.pid
}

func_all() {
  echo "Enter the scenario name (press enter if default):"
  read SCENARIONAME
  if [ -z "$SCENARIONAME" ];
    then
      SCENARIONAME="scenario_example"
  fi
  echo "Enter your jmeter path (Ex:- /home/user/Documents/apache-jmeter-5.1.1/bin)"
  read JMPATH
  echo "Enter filename (without file extension): "
  read FILENAME
  echo "Enter script execution time in minutes: "
  read EXECTIME

  if command -v python3 &>/dev/null; then
    python3 ../lib/traffic-tool/src/python/gen_user_details.py 1

    if [ -e "$(pwd)"/../lib/traffic-tool/data/scenario/$SCENARIONAME/data/api_creation.csv -a -e "$(pwd)"/../lib/traffic-tool/data/scenario/$SCENARIONAME/data/api_creation_swagger.csv -a -e "$(pwd)"/../lib/traffic-tool/data/scenario/$SCENARIONAME/data/app_creation.csv -a -e "$(pwd)"/../lib/traffic-tool/data/scenario/$SCENARIONAME/data/app_api_subscription_admin.csv -a -e "$(pwd)"/../lib/traffic-tool/data/scenario/$SCENARIONAME/data/user_generation.csv -a -e "$(pwd)"/../lib/traffic-tool/data/scenario/$SCENARIONAME/data/user_app_pattern.csv -a -e "$(pwd)"/../lib/traffic-tool/data/scenario/$SCENARIONAME/data/api_invoke_scenario.csv ];
    then
      rm -f ../lib/traffic-tool/data/scenario/$SCENARIONAME/api_invoke_key_secret.csv
      $JMPATH/jmeter -n -t '../lib/traffic-tool/src/jmeter/create_api_scenario.jmx' -l ../logs/jmeter-results.log -j ../logs/jmeter.log

      rm -f ../lib/traffic-tool/data/scenario/$SCENARIONAME/api_invoke_tokens.csv
      $JMPATH/jmeter -n -t '../lib/traffic-tool/src/jmeter/generate_token_list.jmx' -l ../logs/jmeter-results.log -j ../logs/jmeter.log

      python3 ../lib/traffic-tool/src/python/gen_invoke_scenario.py

      if [ -e "$(pwd)"/../lib/traffic-tool/data/scenario/$SCENARIONAME/api_invoke_tokens.csv ];
      then
        chmod +x ../lib/traffic-tool/src/python/invoke_API.py
        nohup python3 ../lib/traffic-tool/src/python/invoke_API.py $FILENAME $EXECTIME >> ../logs/traffic-shell.log 2>&1 &
        echo $! > ../data/traffic_tool.pid
      else
        echo "Missing token file in the 'data/scenario/$SCENARIONAME/' directory"
        exit 1
      fi
    else
      echo "Missing one or more required files in the 'data/scenario/$SCENARIONAME/data/' directory"
      exit 1
    fi
  elif command -v python &>/dev/null; then
    python ../lib/traffic-tool/src/python/gen_user_details.py 1

    if [ -e "$(pwd)"/../lib/traffic-tool/data/scenario/$SCENARIONAME/data/api_creation.csv -a -e "$(pwd)"/../lib/traffic-tool/data/scenario/$SCENARIONAME/data/api_creation_swagger.csv -a -e "$(pwd)"/../lib/traffic-tool/data/scenario/$SCENARIONAME/data/app_creation.csv -a -e "$(pwd)"/../lib/traffic-tool/data/scenario/$SCENARIONAME/data/app_api_subscription_admin.csv -a -e "$(pwd)"/../lib/traffic-tool/data/scenario/$SCENARIONAME/data/user_generation.csv -a -e "$(pwd)"/../lib/traffic-tool/data/scenario/$SCENARIONAME/data/user_app_pattern.csv -a -e "$(pwd)"/../lib/traffic-tool/data/scenario/$SCENARIONAME/data/api_invoke_scenario.csv ];
    then
      rm -f ../lib/traffic-tool/data/scenario/$SCENARIONAME/api_invoke_key_secret.csv
      $JMPATH/jmeter -n -t '../lib/traffic-tool/src/jmeter/create_api_scenario.jmx' -l ../logs/jmeter-results.log -j ../logs/jmeter.log

      rm -f ../lib/traffic-tool/data/scenario/$SCENARIONAME/api_invoke_tokens.csv
      $JMPATH/jmeter -n -t '../lib/traffic-tool/src/jmeter/generate_token_list.jmx' -l ../logs/jmeter-results.log -j ../logs/jmeter.log

      python ../lib/traffic-tool/src/python/gen_invoke_scenario.py

      if [ -e "$(pwd)"/../lib/traffic-tool/data/scenario/$SCENARIONAME/api_invoke_tokens.csv ];
      then
        chmod +x ../lib/traffic-tool/src/python/invoke_API.py
        nohup python ../lib/traffic-tool/src/python/invoke_API.py $FILENAME $EXECTIME >> ../logs/traffic-shell.log 2>&1 &
        echo $! > ../data/traffic_tool.pid
      else
        echo "Missing token file in the 'data/scenario/$SCENARIONAME/' directory"
        exit 1
      fi
    else
      echo "Missing one or more required files in the 'data/scenario/$SCENARIONAME/data/' directory"
      exit 1
    fi
  else
    echo "Python 3 is required for the command!"
    exit 1
  fi
}


case "$1" in
  -h)
    func_help
    exit 0
  ;;
  1)
    func_gen_user_details 2>&1 | tee -a ../logs/traffic-shell.log
    exit 0
  ;;
  2)
    func_gen_example_scenario 2>&1 | tee -a ../logs/traffic-shell.log
    exit 0
  ;;
  3)
    func_create_scenario 2>&1 | tee -a ../logs/traffic-shell.log
    exit 0
  ;;
  4)
    func_gen_tokens 2>&1 | tee -a ../logs/traffic-shell.log
    exit 0
  ;;
  5)
    func_gen_invoke_data 2>&1 | tee -a ../logs/traffic-shell.log
    exit 0
  ;;
  6)
    func_traffic 2>&1 | tee -a ../logs/traffic-shell.log
    exit 0
  ;;
  7)
    func_stop_traffic 2>&1 | tee -a ../logs/traffic-shell.log
    exit 0
  ;;
  all)
    func_all 2>&1 | tee -a ../logs/traffic-shell.log
    exit 0
  ;;
  *)
    echo "Invalid argument!"
    func_help
    exit 1
  ;;
esac
