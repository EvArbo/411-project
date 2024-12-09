#!/bin/bash

#!/bin/bash

# Environment variables
BASE_URL="http://localhost:5000/api"
DB_PATH="/app/db/fitness_tracker.db"
SQL_CREATE_TABLE_PATH="/app/sql/init_db.sql"
CREATE_DB=true
WGER_API_KEY="28f9abfb4e3108279553c836838d34d1b833280f"
WGER_API_URL="https://wger.de/api/v2"
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
# User management
#
##############################################

# Function to create a user
create_user() {
  echo "Creating a new user..."
  curl -s -X POST "$BASE_URL/create-user" -H "Content-Type: application/json" \
    -d '{"username":"testuser", "password":"password123"}' | grep -q '"status": "user added"'
  if [ $? -eq 0 ]; then
    echo "User created successfully."
  else
    echo "Failed to create user."
    exit 1
  fi
}

# Function to log in a user
login_user() {
  echo "Logging in user..."
  response=$(curl -s -X POST "$BASE_URL/login" -H "Content-Type: application/json" \
    -d '{"username":"testuser", "password":"password123"}')
  if echo "$response" | grep -q '"message": "User testuser logged in successfully."'; then
    echo "User logged in successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Login Response JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to log in user."
    if [ "$ECHO_JSON" = true ]; then
      echo "Error Response JSON:"
      echo "$response" | jq .
    fi
    exit 1
  fi
}

# Function to log out a user
logout_user() {
  echo "Logging out user..."
  response=$(curl -s -X POST "$BASE_URL/logout" -H "Content-Type: application/json" \
    -d '{"username":"testuser"}')
  if echo "$response" | grep -q '"message": "User testuser logged out successfully."'; then
    echo "User logged out successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Logout Response JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to log out user."
    if [ "$ECHO_JSON" = true ]; then
      echo "Error Response JSON:"
      echo "$response" | jq .
    fi
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
    echo "Response: $response"
    exit 1
  fi
}

# Exercise Creation Function
create_exercise() {
  name=$1
  weight=$2
  sets=$3
  repetitions=$4
  rpe=$5

  echo "Adding exercise ($name) to the playlist..."
  response=$(curl -s -X POST "$BASE_URL/create-exercise" -H "Content-Type: application/json" \
    -d "{\"name\":\"$name\", \"weight\":\"$weight\", \"sets\":$sets, \"repetitions\":\"$repetitions\", \"rpe\":$rpe}")

  if echo "$response" | grep -q '"status": "success"'; then
    echo "Exercise added successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Create Exercise Response:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to add exercise."
    echo "Response: $response"
    exit 1
  fi
}

# Function to get exercise by ID
get_exercise_by_id() {
  exercise_id=$1

  echo "Retrieving exercise with ID $exercise_id..."
  response=$(curl -s -X GET "$BASE_URL/get-exercise-by-id/$exercise_id")
  
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Exercise retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Exercise JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to retrieve exercise by ID."
    echo "Response: $response"
    exit 1
  fi
}

# Function to get all exercises
get_all_exercises() {
  echo "Retrieving all exercises..."
  response=$(curl -s -X GET "$BASE_URL/get-all-exercises")
  
  if echo "$response" | grep -q '"status": "success"'; then
    echo "All exercises retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "All Exercises JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to retrieve all exercises."
    echo "Response: $response"
    exit 1
  fi
}

# Function to delete exercise by ID
delete_exercise_by_id() {
  exercise_id=$1

  echo "Deleting exercise by ID ($exercise_id)..."
  response=$(curl -s -X DELETE "$BASE_URL/delete-exercise/$exercise_id")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Exercise deleted successfully by ID ($exercise_id)."
    if [ "$ECHO_JSON" = true ]; then
      echo "Delete Exercise Response:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to delete exercise by ID ($exercise_id)."
    echo "Response: $response"
    exit 1
  fi
}

# Function to fetch exercise categories
fetch_exercise_categories() {
  echo "Fetching exercise categories..."
  response=$(curl -s -X GET "$BASE_URL/fetch-exercise-categories")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Exercise categories retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Exercise Categories JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to fetch exercise categories."
    echo "Response: $response"
    exit 1
  fi
}

# Function to fetch muscle groups
fetch_muscles() {
  echo "Fetching muscle groups..."
  response=$(curl -s -X GET "$BASE_URL/fetch-muscles")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Muscle groups retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Muscle Groups JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to fetch muscle groups."
    echo "Response: $response"
    exit 1
  fi
}

# Function to fetch exercises
fetch_exercises() {
  muscle_id=${1:-}
  
  if [ -z "$muscle_id" ]; then
    echo "Fetching all exercises..."
    response=$(curl -s -X GET "$BASE_URL/fetch-exercises")
  else
    echo "Fetching exercises for muscle ID $muscle_id..."
    response=$(curl -s -X GET "$BASE_URL/fetch-exercises?muscle_id=$muscle_id")
  fi
  
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Exercises retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Exercises JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to fetch exercises."
    echo "Response: $response"
    exit 1
  fi
}

# Function to fetch equipment
fetch_equipment() {
  echo "Fetching equipment..."
  response=$(curl -s -X GET "$BASE_URL/fetch-equipment")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Equipment retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Equipment JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to fetch equipment."
    echo "Response: $response"
    exit 1
  fi
}

# Function to fetch exercise images
fetch_exercise_images() {
  echo "Fetching exercise images..."
  response=$(curl -s -X GET "$BASE_URL/fetch-exercise-images")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Exercise images retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Exercise Images JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to fetch exercise images."
    echo "Response: $response"
    exit 1
  fi
}

# Function to get workout summary
get_workout_summary() {
  echo "Getting workout summary..."
  response=$(curl -s -X GET "$BASE_URL/get-workout-summary")
  if echo "$response" | grep -q '"status": "success"'; then
    echo "Workout summary retrieved successfully."
    if [ "$ECHO_JSON" = true ]; then
      echo "Workout Summary JSON:"
      echo "$response" | jq .
    fi
  else
    echo "Failed to get workout summary."
    echo "Response: $response"
    exit 1
  fi
}

# Leaderboard functions
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
    echo "Response: $response"
    exit 1
  fi
}

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
    echo "Response: $response"
    exit 1
  fi
}


  # Run all the steps in order
  check_health
  init_db
  create_user
  login_user

  # Create exercises
  create_exercise "Barbell Deadlift" 315 4 2 7
  create_exercise "Barbell Bench Press" 225 5 3 8
  create_exercise "Barbell Squat" 275 4 4 7
  create_exercise "Barbell Overhead Press" 135 3 3 6
  create_exercise "Pull-Up" 0 4 4 8

  # Retrieve and manipulate exercises
  get_exercise_by_id 1
  get_all_exercises
  delete_exercise_by_id 1

  # Fetch additional data
  # fetch_exercise_categories
  # fetch_muscles
  # fetch_exercises  # Fetches all exercises
  # # Uncomment the line below to fetch exercises for a specific muscle ID
  # # fetch_exercises 1
  # fetch_equipment
  # fetch_exercise_images
  get_workout_summary
  logout_user



  echo "All tests passed successfully!"


