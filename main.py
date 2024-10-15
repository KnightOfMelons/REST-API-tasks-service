from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime, timezone

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI',
                                                  'postgresql://postgres:123456789qwe123!'
                                                  '@localhost/tasksdb')
db = SQLAlchemy(app)


class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    description = db.Column(db.Text, nullable=False)  # Исправлено: nullable вместо nullabe
    status = db.Column(db.String(20), default='new', nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc),
                           onupdate=lambda: datetime.now(timezone.utc))



with app.app_context():
    db.create_all()


@app.route('/tasks', methods=['POST'])
def create_task():
    description = request.json.get('description')
    task = Task(description=description)
    db.session.add(task)
    db.session.commit()
    return jsonify({'id': task.id,
                    'status': task.status}), 201


@app.route('/tasks/<int:task_id>', methods=['GET'])
def get_task(task_id):
    task = Task.query.get_or_404(task_id)
    return jsonify({'id': task.id,
                    'description': task.description,
                    'status': task.status})


@app.route('/tasks', methods=['GET'])
def list_tasks():
    status_filter = request.args.get('status')
    tasks_query = Task.query
    if status_filter:
        tasks_query = tasks_query.filter_by(statu=status_filter)
    tasks = tasks_query.all()
    return jsonify([{'id': task.id,
                     'description': task.description,
                     'status': task.status} for task in tasks])


if __name__ == "__main__":
    app.run(debug=True)
