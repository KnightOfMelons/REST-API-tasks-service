import json
import os
import pika
from flask import Flask, request, jsonify
from flasgger import Swagger, swag_from
from models import db, Task

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI',
                                                  'postgresql://postgres:123456789qwe123!@db/tasksdb')

swagger = Swagger(app)

db.init_app(app)

with app.app_context():
    db.create_all()


def send_task_to_queue(task_id, description):
    connection = pika.BlockingConnection(pika.ConnectionParameters('rabbitmq'))
    channel = connection.channel()

    channel.queue_declare(queue='task_queue', durable=True)

    message = json.dumps({
        'task_id': task_id,
        'description': description
    })

    channel.basic_publish(
        exchange='',
        routing_key='task_queue',
        body=message,
        properties=pika.BasicProperties(
            delivery_mode=2,
        )
    )

    connection.close()


@app.route('/tasks', methods=['POST'])
@swag_from({
    'responses': {
        201: {
            'description': 'Task created successfully',
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer'},
                    'description': {'type': 'string'},
                    'status': {'type': 'string'}
                }
            }
        },
        400: {
            'description': 'Invalid input'
        }
    },
    'parameters': [
        {
            'name': 'task',
            'in': 'body',
            'schema': {
                'type': 'object',
                'properties': {
                    'description': {'type': 'string', 'example': 'Test task'}
                },
                'required': ['description']
            }
        }
    ]
})
def create_task():
    description = request.json.get('description')
    task = Task(description=description)
    db.session.add(task)
    db.session.commit()

    send_task_to_queue(task.id, task.description)

    return jsonify({"id": task.id, "status": task.status}), 201


@app.route('/tasks/<int:task_id>', methods=['GET'])
@swag_from({
    'parameters': [
        {
            'name': 'task_id',
            'in': 'path',
            'type': 'integer',
            'required': True,
            'description': 'ID of the task to retrieve'
        }
    ],
    'responses': {
        200: {
            'description': 'Task found',
            'schema': {
                'type': 'object',
                'properties': {
                    'id': {'type': 'integer'},
                    'description': {'type': 'string'},
                    'status': {'type': 'string'}
                }
            }
        },
        404: {
            'description': 'Task not found'
        }
    }
})
def get_task(task_id):
    task = Task.query.get_or_404(task_id)
    return jsonify({'id': task.id,
                    'description': task.description,
                    'status': task.status})


@app.route('/tasks', methods=['GET'])
@swag_from({
    'responses': {
        200: {
            'description': 'List of tasks',
            'schema': {
                'type': 'array',
                'items': {
                    'type': 'object',
                    'properties': {
                        'id': {'type': 'integer'},
                        'description': {'type': 'string'},
                        'status': {'type': 'string'}
                    }
                }
            }
        }
    }
})
def list_tasks():
    status_filter = request.args.get('status')
    tasks_query = Task.query
    if status_filter:
        tasks_query = tasks_query.filter_by(status=status_filter)
    tasks = tasks_query.all()
    return jsonify([{'id': task.id,
                     'description': task.description,
                     'status': task.status} for task in tasks])


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5000)
