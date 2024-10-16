import pika
import json
import logging
import time
import random
import os
from models import Task
from main import app, db

# Настройка логирования
logging.basicConfig(level=logging.INFO)


# Тут эмуляция обработки задачи
def process_task(task_data):
    with app.app_context():
        task = db.session.get(Task, task_data['task_id'])
        if task is None:
            logging.error(f"Задача ID: {task_data['task_id']} не найдена.")
            return

        logging.info(f"Обработка задачи ID: {task.id}")
        task.status = 'in_progress'
        db.session.commit()

        # Эмуляция времени обработки
        time.sleep(random.randint(5, 10))  # Задержка на 5-10 секунд

        try:
            if random.random() < 0.8:
                task.status = 'completed'  # 80% шанса на успех
                logging.info(f"Задача ID: {task.id} завершена успешно.")
            else:
                raise Exception("Ошибка при обработке задачи.")  # Принудительная ошибка для тестирования

        except Exception as e:
            task.status = 'error'  # 20% шанса на ошибку
            logging.error(f"Задача ID: {task.id} завершилась с ошибкой: {str(e)}")

        finally:
            db.session.commit()  # Коммитим изменения независимо от результата


def callback(ch, method, _, body):
    task_data = json.loads(body)
    logging.info(f"Получена задача: {task_data}")

    process_task(task_data)

    ch.basic_ack(delivery_tag=method.delivery_tag)


def start_worker():
    rabbitmq_host = os.getenv('RABBITMQ_HOST', 'rabbitmq')  # По умолчанию 'rabbitmq'
    connection = pika.BlockingConnection(pika.ConnectionParameters(rabbitmq_host))

    channel = connection.channel()

    channel.queue_declare(queue='task_queue', durable=True)

    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='task_queue', on_message_callback=callback)

    logging.info("Ожидание задач...")
    channel.start_consuming()


if __name__ == "__main__":
    start_worker()
