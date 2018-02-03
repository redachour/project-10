from flask import Flask, g, jsonify, render_template

import models
from auth import auth
from resources.todos import todos_api

app = Flask(__name__)
app.register_blueprint(todos_api, url_prefix='/api/v1')


@app.route('/')
def my_todos():
    return render_template('index.html')


@app.route('/api/v1/users/token', methods=['GET'])
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token()
    return jsonify({'token': token.decode('ascii')})


if __name__ == '__main__':
    models.initialize()
    try:
        models.User.create_user(
            username='username',
            password='password')
    except Exception:
        pass
    app.run(debug=True)
