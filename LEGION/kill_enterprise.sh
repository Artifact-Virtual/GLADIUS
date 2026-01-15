#!/bin/bash
# filepath: kill_ports.sh

for port in 3000 5000 5001 8000 8080 9000 27017 6379 3306 5432; do
  echo "Killing processes on port $port..."
  fuser -k ${port}/tcp
  # Optionally, try lsof for stubborn processes
  # lsof -ti tcp:${port} | xargs -r kill -9
  # Optionally, try killall for named processes
  # killall -q -w node python3 mongod redis-server mysqld postgres
  # Uncomment above lines for more aggressive cleanup
  sleep 0.2
  # Add a short delay for safety
  
done

# Deactivate any active virtual environments
if [[ "$VIRTUAL_ENV" != "" ]]; then
  echo "Deactivating virtual environment: $VIRTUAL_ENV"
  deactivate
fi

echo "Done."