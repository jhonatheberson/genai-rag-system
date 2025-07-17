#!/bin/bash

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."
while ! nc -z postgres 5432; do
  sleep 0.1
done
echo "PostgreSQL is ready!"


# Run migrations
echo "Running database migrations..."
export PATH="$PATH:/root/.dotnet/tools"
dotnet-ef database update --project src/Infrastructure --startup-project src/API

# Start the API
echo "Starting the API..."
dotnet API.dll