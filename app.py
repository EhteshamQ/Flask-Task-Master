from datetime import datetime
from flask import Flask, redirect, render_template, request
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///test.db"
db = SQLAlchemy(app)


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)
    complete = db.Column(db.Integer, default=0)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Task {self.id}>"


@app.route("/", methods=["POST", "GET"])
def index():
    if request.method == "POST":
        task_content = request.form["content"]
        new_task = Todo(content=task_content)

        try:
            db.session.add(new_task)
            db.session.commit()
            return redirect("/")
        except Exception as e:
            print(e)
            return "There was an issue adding your task"
    else:
        tasks = Todo.query.order_by(Todo.date_created).all()
        return render_template("index.html", tasks=tasks)


@app.route("/tasks/delete/<int:id>")
def tasks_route(id: int):
    try:
        task = Todo.query.get_or_404(id)
        if task is None:
            return "There is no element with this id"
        else:
            db.session.delete(task)
            db.session.commit()
            return redirect("/")

    except Exception as e:
        print(e)
        return "There was an error performing delete operation"


@app.route("/tasks/update/<int:id>", methods=["GET", "POST"])
def update_task(id: int):
    task = Todo.query.get_or_404(id)
    if request.method == "POST":
        if task is None:
            return redirect("/")
        task.content = request.form["new_content"]
        db.session.commit()
        return redirect("/")
    else:
        if task is None:
            return redirect("/")
        return render_template("update.html", task=task)


@app.route("/tasks/check/<int:id>", methods=["PATCH"])
def check_task(id: int):
    try:
        task = Todo.query.get_or_404(id)
        if task is None:
            return "There is no element with this id"
        else:
            task.complete = 1 if int(request.args["checked"]) == 1 else 0
            db.session.commit()
            return "", 200
    except Exception as e:
        print(e)
        return "There was an error performing delete operation"


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
    app.run(debug=True)
