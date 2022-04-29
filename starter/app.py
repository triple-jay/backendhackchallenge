import json
import users_dao
import datetime

from db import db, User, Task
from flask import Flask, request

db_filename = "auth.db"
app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///%s" % db_filename
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True

db.init_app(app)
with app.app_context():
    db.create_all()


# generalized response formats
def success_response(data, code=200):
    """
    Generalized success response function
    """
    return json.dumps(data), code

def failure_response(message, code=404):
    """
    Generalized failure response function
    """
    return json.dumps({"error": message}), code


def extract_token(request):
    """
    Helper function that extracts the token from the header of a request
    """
    auth_header = request.headers.get('Authorization')
    if auth_header is None:
        return False, json.dumps({'Missing authorization token'})
    
    bearer_token = auth_header.replace('Bearer', '').strip()

    return True, bearer_token


@app.route("/")
def hello_world():
    """
    Endpoint for printing Hello World!
    """
    return "Hello World!"


@app.route("/register/", methods=["POST"])
def register_account():
    """
    Endpoint for registering a new user with email and password from post
    """
    body = json.loads(request.data)
    username = body.get('username')
    password = body.get('password')

    if username is None or password is None:
        return failure_response('Missing username or password')

    # since create_user returns a 2-ple
    was_successful, user = users_dao.create_user(username, password)

    if not was_successful:
        return failure_response('User already exists')
    return success_response(
        {
            'session_token': user.session_token,
            'session_expiration': str(user.session_expiration),
            'update token': user.update_token

        }, 201
    )


@app.route("/login/", methods=["POST"])
def login():
    """
    Endpoint for logging in a user
    """
    body = json.loads(request.data)
    username = body.get('username')
    password = body.get('password')

    if username is None or password is None:
        return failure_response('Missing email or password', 400)

    was_successful, user = users_dao.verify_credentials(username, password)
    if not was_successful:
        return failure_response('Incorrect username or password', 401)

    return success_response(
        {
            'session_token': user.session_token,
            'session_expiration': str(user.session_expiration),
            'update_token': user.update_token
        }
    )


@app.route("/session/", methods=["POST"])
def update_session():
    """
    Endpoint for updating a user's session
    """
    was_successful, update_token = extract_token(request)

    if not was_successful:
        return update_token
    
    try:
        user = users_dao.renew_session(update_token)
    except Exception as e:
        return failure_response(f'Invalid update token: {str(e)}')

    return success_response(
        {
            'session_token': user.session_token,
            'session_expiration': str(user.session_expiration),
            'update_token': user.update_token
        }
    )


@app.route("/secret/", methods=["GET"])
def secret_message():
    """
    Endpoint for verifying a session token and returning a secret message

    In your project, you will use the same logic for any endpoint that needs 
    authentication
    """
    was_successful, session_token = extract_token(request)

    if not was_successful:
        return session_token
    
    user = users_dao.get_user_by_session_token(session_token)
    if not user or not user.verify_session_token(session_token):
        return failure_response('Invalid session token')
    
    return success_response({'message': 'You have successfully implemented a session!'})

@app.route('/logout/', methods = ['POST'])
def logout():
    was_successful, session_token = extract_token(request)

    if not was_successful:
        return session_token

    user = users_dao.get_user_by_session_token(session_token)

    if not user or not user.verify_session_token(session_token):
        return failure_response('Invalid session token')
    
    user.session_expiration = datetime.datetime.now()
    db.session.commit()

    return success_response(
        {
            'message': 'You have logged out'
        }
    )

@app.route('/tasks/add/', methods = ['POST'])
def add_task():
    '''
    given a session_token, get the user associated with it
    make a Task assigned to User
    '''
    was_successful, session_token = extract_token(request)

    if not was_successful:
        return session_token

    user = users_dao.get_user_by_session_token(session_token)
    if not user or not user.verify_session_token(session_token):
        return failure_response('Invalid session token')
    
    body = json.loads(request.data)
    task_name = body.get('task_name','')
    due_date = datetime.datetime.now()
    completed = body.get('done', 0)
    priority = body.get('priority', 0)
    user_id = user.id

    if task_name is None:
        return failure_response('task_name is none.', 401)
    
    new_task = Task(
        user_id = user_id,
        task_name = task_name,
        due_date = due_date,
        completed = completed,
        priority = priority
    )
    db.session.add(new_task)
    db.session.commit()
    return success_response(new_task.serialize(), 201)

@app.route('/tasks/')
def get_tasks():
    '''
    given a session_token, get a user, get all tasks for that User
    '''

    was_successful, session_token = extract_token(request)

    if not was_successful:
        return session_token

    user = users_dao.get_user_by_session_token(session_token)
    if not user or not user.verify_session_token(session_token):
        return failure_response('Invalid session token')

    return success_response(user.get_all_tasks())

@app.route('/tasks/<int:user_id>/<int:task_id>/')
def get_task_by_id(user_id, task_id):
    task = Task.query.filter_by(id = task_id).first()
    if task is None:
        return failure_response('Task not found')
    return success_response(task.serialize())

@app.route('/tasks/<int:task_id>/', methods = ['POST'])
def update_task(task_id):
    '''
    given task_id, update the fields of the Task object
    '''
    task = Task.query.filter_by(id = task_id).first()
    if task is None:
        return failure_response('Task not found')

    body = json.loads(request.data)
    title = body.get('title')
    description = body.get('description')
    time = body.get('time')
    done = body.get('done')

    '''
    update fields if they are supplied (not null)
    '''
    if title is not None:
        task.title = title
    if description is not None:
        task.description = description
    if time is not None:
        task.time = time
    if done is not None:
        task.done = done
    
    db.session.commit()
    return success_response(task.serialize())

@app.route('/tasks/<int:user_id>/<int:task_id>/', methods = ['DELETE'])
def delete_task(user_id, task_id):
    '''
    given user_id and task_id via URL, delete the task for this user
    '''
    user = User.query.filter_by(id = user_id).first()
    if user is None:
        return failure_response('User not found')

    task = Task.query.filter_by(id = task_id).first()
    if task is None:
        return failure_response('Task not found')
    
    db.session.delete(task)
    db.session.commit()
    return success_response(task.serialize())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
