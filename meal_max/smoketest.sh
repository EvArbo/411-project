#!/bin/bash

# Define the base URL for the Flask API
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
# Health checks
#
###############################################

# Function to check the health of the service
check_health() {
  echo "Checking health status..."
  curl -s -X GET "$BASE_URL/health" | grep -q '"status": "healthy"'
  if [ $? -eq 0 ]; then
    echo "Service is healthy."
  else
    echo "Health check failed."
    exit 1
  fi
}

##############################################
#
# Exercises
#
##############################################

# Function to add a exercise 
create_exercise() {
  name=$1
  weight=$2
  sets=$3
  repetitions=$4
  rpe=$5

  echo "Adding exercise ($name) to the playlist..."
  curl -s -X POST "$BASE_URL/create-exercise" -H "Content-Type: application/json" \
    -d "{\"name\":\"$name\", \"weight\":\"$weight\", \"sets\":$sets, \"repetitions\":\"$repetitions\", \"rpe\":$rpe}" | grep -q '"status": "success"'

  if [ $? -eq 0 ]; then
    echo "Exercise added successfully."
  else
    echo "Failed to add exercise."
    exit 1
  fi
}

# Function to delete a exercise by ID (1)
delete_exercise_by_id() {
  exercise_id=$1

  echo "Deleting exercise by ID ($exercise_id)..."
  response=$(curl -s -X DELETE "$BASE_URL/delete-exercise/$exercise_id")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Exercise deleted successfully by ID ($exercise_id)."
  else
    echo "Failed to delete exercise by ID ($exercise_id)."
    exit 1
  fi
}

get_all_exercises() {
  echo "Getting all exercises..."
  response=$(curl -s -X GET "$BASE_URL/get-all-exercises-from-catalog")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "All exercises retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Exercises JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get exercises."
    exit 1
  fi
}
# Function to get a exercise by ID (1)
get_exercise_by_id() {
  exercises_id = $1
  echo "Getting exercise by ID (1)..."
  response=$(curl -s -X GET "$BASE_URL/get-exercise-from-catalog-by-id/1")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "exercise retrieved successfully by ID (1)."
    if [ "$ECHO_JSON" = true ]; then
      echo "exercise JSON (ID 1):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get exercise by ID (1)."
    exit 1
  fi
}


######################################################
#
# Leaderboard
#
######################################################

# Function to get the leaderboard sorted by wins
get_leaderboard_wins() {
  echo "Getting leaderboard sorted by wins..."
  response=$(curl -s -X GET "$BASE_URL/leaderboard?sort=wins")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Leaderboard by wins retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Leaderboard JSON (sorted by wins):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get leaderboard by wins."
    exit 1
  fi
}

# Function to get the leaderboard sorted by win percentage
get_leaderboard_win_pct() {
  echo "Getting leaderboard sorted by win percentage..."
  response=$(curl -s -X GET "$BASE_URL/leaderboard?sort=win_pct")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Leaderboard by win percentage retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Leaderboard JSON (sorted by win percentage):"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get leaderboard by win percentage."
    exit 1
  fi
}

# Function to initialize the database
init_db() {
  echo "Initializing the database..."
  response=$(curl -s -X POST "$BASE_URL/init-db")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Database initialized successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Initialization Response JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to initialize the database."
    exit 1
  fi
}



# Run all the steps in order
check_health
init_db
create_user
login_user


create_exercise "Barbell Deadlift" 315 4 2 7
create_exercise "Barbell Bench Press" 225 5 3 8
create_exercise "Barbell Squat" 275 4 4 7
create_exercise "Barbell Overhead Press" 135 3 3 6
create_exercise "Pull-Up" 0 4 4 8

get_exercise_by_id 1

get_all_exercises

delete_exercise_by_id 1





echo "All tests passed successfully!"
