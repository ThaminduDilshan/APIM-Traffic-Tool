#!/bin/sh

func_help() {
  echo "Attack Tool Options"
  echo "1: DOS Attack"
  echo "2: DDOS Attack"
}

func_DOS() {
  echo "Enter your jmeter path (Ex:- /home/user/Documents/apache-jmeter-5.1.1/bin)"
    read JMPATH
    $JMPATH/jmeter -n -t '../lib/attack-tool/src/jmeter/DOS_Attack.jmx' -l ../logs/jmeter-attack-results.log -j ../logs/jmeter-attack.log
    echo $! > ../data/attack_tool.pid
}

func_DDOS() {
  echo "Enter your jmeter path (Ex:- /home/user/Documents/apache-jmeter-5.1.1/bin)"
    read JMPATH
    $JMPATH/jmeter -n -t '../lib/attack-tool/src/jmeter/DDOS_Attack.jmx' -l ../logs/jmeter-attack-results.log -j ../logs/jmeter-attack.log
    echo $! > ../data/attack_tool.pid
}

func_stop_attack() {
  PID=`cat ../data/attack_tool.pid 2>/dev/null`
  if [ -z $PID ];
  then
    echo "Attack Tool is Not Running"
  else
    kill -0 $PID 2>/dev/null
    if [ $? -eq 0 ];
    then
      kill -9 $PID
      if [ $? -eq 0 ];
      then
          echo "Attack Tool Stopped Successfully"
      fi
    else
      echo "Attack Tool Already Stopped"
    fi
  fi > ../data/attack_tool.pid
}


case "$1" in
  -h)
    func_help
    exit 0
  ;;
  1)
    func_DOS | tee -a ../logs/attack-shell.log
    exit 0
  ;;
  2)
    func_DDOS | tee -a ../logs/attack-shell.log
    exit 0
  ;;
  3)
    func_stop_attack | tee -a ../logs/attack-shell.log
    exit 0
  ;;
  *)
    echo "Invalid argument!"
    func_help
    exit 1
  ;;
esac
