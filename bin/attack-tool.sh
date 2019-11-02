#!/bin/sh

func_help() {
  echo "Attack Tool Options"
  echo "1: description"
}

func_() {
  
}


case "$1" in
  -h)
    func_help
    exit 0
  ;;
  1)
    func_ | tee -a ./logs/attack-shell.log
    exit 0
  ;;
  *)
    echo "Invalid argument!"
    func_help
    exit 1
  ;;
esac
