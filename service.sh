#!/bin/bash
# This script will search for 'airflow scheduler' processes and attempt to terminate them gracefully.

# Search for Airflow scheduler processes, excluding the grep command itself using grep -v grep
# Then use awk to print the second column which contains the PID
S_PIDS=$(ps aux | grep "airflow scheduler" | grep -v grep | awk '{print $2}')

# Check if any PIDs were found
if [ -z "$S_PIDS" ]; then
  echo "No Airflow scheduler processes found."
else   
  # Attempt to terminate each found PID gracefully
  for PID in $S_PIDS; do
    echo "Terminating Airflow scheduler process with PID: $PID"
    kill $PID

    # Check if the process was terminated successfully
    if [ $? -eq 0 ]; then
      echo "Successfully terminated process $PID."
    else
      echo "Failed to terminate process $PID. You might need to run the script as root or use a stronger signal."
    fi
  done

  echo "All Airflow scheduler processes have been terminated."
fi

echo ""

W_PIDS=$(ps aux | grep "airflow webserver" | grep -v grep | awk '{print $2}')

# Check if any PIDs were found
if [ -z "$W_PIDS" ]; then
  echo "No Airflow webserver processes found."
else
    # Attempt to terminate each found PID gracefully
    for PID in $W_PIDS; do
    echo "Terminating Airflow webserver process with PID: $PID"
    kill $PID

    # Check if the process was terminated successfully
    if [ $? -eq 0 ]; then
        echo "Successfully terminated process $PID."
    else
        echo "Failed to terminate process $PID. You might need to run the script as root or use a stronger signal."
    fi
    done

    echo "All Airflow webserver processes have been terminated."
fi

if [ "$1" != "stop" ]; then
  # `nohup`: This is a command that is used to run another command in the background, ignoring the HUP (hangup) signal. The HUP signal is sent to the process when its controlling terminal is closed. By ignoring this signal, nohup ensures that the Airflow webserver continues running even if you log out or close the terminal.
  # `airflow webserver -p 8080`: This is the command to start the Airflow webserver on port 8080. Airflow is a platform to programmatically author, schedule, and monitor workflows. The webserver provides a web-based user interface to inspect, trigger, and debug the workflows.
  # `airflow scheduler`: This command starts the Airflow scheduler, a core component of Apache Airflow that monitors all tasks and DAGs (Directed Acyclic Graphs), triggers the task instances whose dependencies have been met, and ensures that the configuration and scheduling are correctly managed and executed.
  # `> webserver.log`: This part redirects the standard output (stdout) of the Airflow webserver process to a file named webserver.log. This means that any output that would normally be printed to the terminal will instead be saved to this file.
  # `2>&1`: This redirects the standard error (stderr) to the same destination as the standard output (stdout), which in this case is the webserver.log file. Essentially, it means both the standard output and standard error of the Airflow webserver will be captured in webserver.log.
  # `&`: This character is used at the end of a command to run it in the background. It allows you to continue using the terminal for other commands while the Airflow webserver runs independently.
  # So, the entire command starts the Airflow webserver and scheduler in the background, ensures it keeps running even if the terminal is closed, and logs all output and errors to webserver.log.
  # export AIRFLOW_HOME=~/Workspace/DIY/Airflow
  export AIRFLOW_HOME=~/Public/webscrape/airflow
  export AIRFLOW__CORE__LOAD_EXAMPLES=false
  nohup airflow scheduler > scheduler.log 2>&1 &
  echo "Running airflow scheduler"
  nohup airflow webserver -p 8080 > webserver.log 2>&1 &
  echo "Running airflow webserver on port 8080"
fi
