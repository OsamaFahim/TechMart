#!/usr/bin/env bash
# filepath: d:\SageTech_Assignment\backend\Techmart\wait-for-it.sh

# I use this script to wait for a TCP host:port to become available before running a command.
# I use this in Docker Compose to make sure the backend only starts after the DB is ready.

set -e  # I want the script to exit immediately if any command fails.

echo "wait-for-it.sh arguments: $@"

host="$1"   # I take the first argument as the host to check (e.g., 'db')
shift
port="$1"   # I take the second argument as the port to check (e.g., '3306')
shift

timeout=15  # By default, I will wait up to 15 seconds (can be overridden by --timeout)
strict=""   # If --strict is set, I will fail if the service isn't ready in time
cmd=""      # This will hold the command I want to run after the service is ready

# I parse additional arguments for timeout, strict mode, and the command to run
while [[ $# -gt 0 ]]
do
    key="$1"
    case $key in
        --timeout)
        timeout="$2"   # If I see --timeout, I use the next argument as the timeout value
        shift; shift
        ;;
        --timeout=*)
        timeout="${key#*=}"  # If I see --timeout=60, I extract 60
        shift
        ;;
        --strict)
        strict="--strict"  # If I see --strict, I remember to fail if the service isn't ready
        shift
        ;;
        --)
        shift
        cmd="$@"   # Everything after -- is the command I want to run
        break
        ;;
        *)
        shift      # I ignore any unknown arguments
        ;;
    esac
done

echo "Waiting for $host:$port for $timeout seconds..."

for i in $(seq $timeout); do
    if nc -z "$host" "$port"; then
        echo "$host:$port is available!"
        exec $cmd
        exit 0
    fi
    sleep 1
done

echo "Timeout after $timeout seconds waiting for $host:$port"
if [ "$strict" = "--strict" ]; then
    exit 1
fi

exec $cmd