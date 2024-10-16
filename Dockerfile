FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
ENV SQLALCHEMY_DATABASE_URI=postgresql://postgres:123456789qwe123!@db:5432/tasks_db
EXPOSE 5000
CMD ["python", "main.py"]
