import json
from db import db
from db import User
from db import Task
from db import Event
from flask import Flask
from flask import request

# define db filename
app = Flask(__name__)
db_filename = "cms.db"

# setup config
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///%s" % db_filename
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True

# initialize app
db.init_app(app)
with app.app_context():
    db.create_all()

# generalized response formats
def success_response(data, code=200):
    return json.dumps(data), code

def failure_response(message, code=404):
    return json.dumps({"error": message}), code

# -- USER ROUTES ------------------------------------------------------
@app.route("/api/users/<int:user_id>/")
def get_user(user_id):
    """
    Endpoint for getting a user by user_id
    """
    user = User.query.filter_by(id=user_id).first()
    if user is None:
        return failure_response("User not found")
    return success_response(user.serialize())


# -- TASK ROUTES ------------------------------------------------------
@app.route("/api/users/<int:user_id>/task/", methods=["POST"])
def create_task_for_user(user_id):
    """Create a task for a user"""
    body = json.loads(request.data)
    user = User.query.filter_by(id = user_id).first()
    if user is None:
        return failure_response("User not found")
    task_name = body.get("task_name")
    if task_name is None:
        return failure_response("task_name not provided", 400)  
    due_date = body.get("due_date")
    if due_date is None:
        return failure_response("due_date not provided", 400)
    completed = body.get("completed")
    if completed is None:
        return failure_response("completed field not provided", 400)
    priority = body.get("priority")
    if priority is None:
        return failure_response("priority not provided", 400)
    task = Task(task_name=task_name, due_date=due_date,completed=completed, priority=priority, user_id=user_id)
    db.session.add(task)
    db.session.commit()
    return success_response(task.serialize(), 201)

@app.route("/api/tasks/<int:task_id>/", methods=["POST"])
def update_task(task_id):
    """"
    Endpoint for updating a task by id
    """
    body = json.loads(request.data)
    task = Task.query.filter_by(id=task_id).first() 
    if task is None:
        return failure_response("Task not found")
    task.description = body.get("description", task.description)
    task.completed = body.get("completed", task.completed)
    db.session.commit()
    return success_response(task.serialize())



    
        



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)