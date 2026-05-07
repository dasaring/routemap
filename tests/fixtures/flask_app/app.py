from flask import Flask, jsonify, request

app = Flask(__name__)


@app.route('/users', methods=['GET'])
def list_users():
    return jsonify([])


@app.route('/users', methods=['POST'])
def create_user():
    data = request.json
    return jsonify(data), 201


@app.route('/users/<int:user_id>', methods=['GET'])
def get_user(user_id):
    return jsonify({'id': user_id})


@app.route('/users/<int:user_id>', methods=['PUT', 'PATCH'])
def update_user(user_id):
    data = request.json
    return jsonify(data)


@app.route('/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    return '', 204


@app.route('/health')
def health_check():
    return jsonify({'status': 'ok'})


if __name__ == '__main__':
    app.run(debug=True)
