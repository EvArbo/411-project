from flask import Flask, jsonify, request, make_response

app = Flask(__name__)

# In-memory storage
workout_sessions = {}
next_session_id = 1

@app.route('/api/create-workout-session', methods=['POST'])
def create_workout_session():
    global next_session_id
    session_data = request.json
    session_data['id'] = next_session_id
    workout_sessions[next_session_id] = session_data
    next_session_id += 1
    return make_response(jsonify({'status': 'success', 'data': session_data}), 201)

@app.route('/api/retrieve-workout-session/<int:session_id>', methods=['GET'])
def retrieve_workout_session(session_id):
    session = workout_sessions.get(session_id)
    if session:
        return make_response(jsonify({'status': 'success', 'data': session}), 200)
    return make_response(jsonify({'status': 'error', 'message': 'Session not found'}), 404)

@app.route('/api/update-workout-session/<int:session_id>', methods=['PUT'])
def update_workout_session(session_id):
    session_data = request.json
    if session_id in workout_sessions:
        workout_sessions[session_id].update(session_data)
        return make_response(jsonify({'status': 'success', 'data': workout_sessions[session_id]}), 200)
    return make_response(jsonify({'status': 'error', 'message': 'Session not found'}), 404)

@app.route('/api/delete-workout-session/<int:session_id>', methods=['DELETE'])
def delete_workout_session(session_id):
    if session_id in workout_sessions:
        del workout_sessions[session_id]
        return make_response(jsonify({'status': 'success', 'message': 'Session deleted'}), 204)
    return make_response(jsonify({'status': 'error', 'message': 'Session not found'}), 404)

@app.route('/api/list-workout-sessions', methods=['GET'])
def list_workout_sessions():
    return make_response(jsonify({'status': 'success', 'data': list(workout_sessions.values())}), 200)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
