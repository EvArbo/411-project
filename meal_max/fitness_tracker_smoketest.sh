#!/bin/bash

# Base URL of the Flask API
BASE_URL="http://localhost:5000/api"

# Flag to control whether to echo JSON output
ECHO_JSON=false

# Parse command-line arguments
while [ "$#" -gt 0 ]; do
  case $1 in
    --echo-json) ECHO_JSON=true ;;
    *) echo "Unknown parameter passed: $1"; exit 1 ;;
  esac
  shift
done

###############################################
#
# Utility Functions
#
###############################################

# Print JSON response if enabled
print_json() {
  if [ "$ECHO_JSON" = true ]; then
    echo "$1" | jq .
  fi
}

# Check API response for success
check_response() {
  if echo "$1" | grep -q '"status": "success"'; then
    echo "Operation succeeded."
    print_json "$1"
  else
    echo "Operation failed."
    print_json "$1"
    exit 1
  fi
}

###############################################
#
# Health Check
#
###############################################

check_health() {
  echo "Checking API health..."
  response=$(curl -s -X GET "$BASE_URL/health")
  if echo "$response" | grep -q '"status": "healthy"'; then
    echo "API is healthy."
    print_json "$response"
  else
    echo "API health check failed."
    print_json "$response"
    exit 1
  fi
}

###############################################
#
# Workout Session Tests
#
###############################################

create_workout_session() {
  echo "Creating a workout session..."
  response=$(curl -s -X POST "$BASE_URL/create-workout-session" -H "Content-Type: application/json" \
    -d '{
      "workout": 1,
      "date": "2024-12-08",
      "notes": "Smoketest workout session",
      "impression": "3",
      "time_start": "10:00:00",
      "time_end": "11:00:00"
    }')
  check_response "$response"
}

retrieve_workout_session() {
  session_id=$1
  echo "Retrieving workout session with ID $session_id..."
  response=$(curl -s -X GET "$BASE_URL/retrieve-workout-session/$session_id")
  check_response "$response"
}

update_workout_session() {
  session_id=$1
  echo "Updating workout session with ID $session_id..."
  response=$(curl -s -X PUT "$BASE_URL/update-workout-session/$session_id" -H "Content-Type: application/json" \
    -d '{
      "workout": 1,
      "date": "2024-12-08",
      "notes": "Updated smoketest workout session",
      "impression": "4",
      "time_start": "10:30:00",
      "time_end": "11:30:00"
    }')
  check_response "$response"
}

delete_workout_session() {
  session_id=$1
  echo "Deleting workout session with ID $session_id..."
  response=$(curl -s -X DELETE "$BASE_URL/delete-workout-session/$session_id")
  if [ -z "$response" ]; then
    echo "Workout session deleted successfully (no content)."
  else
    echo "Failed to delete workout session."
    print_json "$response"
    exit 1
  fi
}

list_workout_sessions() {
  echo "Listing all workout sessions..."
  response=$(curl -s -X GET "$BASE_URL/list-workout-sessions")
  check_response "$response"
}

###############################################
#
# Database Initialization
#
###############################################

initialize_database() {
  echo "Initializing database..."
  response=$(curl -s -X POST "$BASE_URL/init-db")
  check_response "$response"
}

###############################################
#
# Run Smoketests
#
###############################################

echo "Starting smoketest..."

# Health check
check_health

# Database initialization
initialize_database

# Create a workout session
create_workout_session

# Retrieve a workout session (assuming ID 1 exists after creation)
retrieve_workout_session 1

# Update the workout session
update_workout_session 1

# List all workout sessions
list_workout_sessions

# Delete the workout session
delete_workout_session 1

# Final health check
check_health

echo "Smoketest completed successfully."
