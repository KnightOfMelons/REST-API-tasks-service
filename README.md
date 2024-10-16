Сначала скопируйте проект в любое удобное место:

```
git clone https://github.com/KnightOfMelons/REST-API-tasks-service.git
```

Затем для сборки и последующего запуска используйте Docker:

```
docker-compose up --build
```

Проект будет доступен по этому адресу:

```
http://localhost:5000
```

Я использовал RabbitMQ, доступ к нему по этому адресу:

```
http://localhost:15672
```

Пользователь и пароль: guest

Также я использовал Swagger, доступ к нему есть через apidocs:

```
http://localhost:5000/apidocs
```

Если лень тестировать через Swager, то можете попробовать через Postman
с разными методами. Типа POST или GET http://localhost:5000/tasks со значениями в Body:

```
{
  "description": "Test task"
}
```

<hr>

Если с Docker ничего не получилось и вы всё-таки хотите запустить проект, то делайте также:
```
git clone https://github.com/KnightOfMelons/REST-API-tasks-service.git
```

Затем создайте свою базу данных PostgreSQL и занесите её в main.py в строчку:

```
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI',
                                                  'postgresql://НИКНЕЙМ:ПАРОЛЬ@db/НАЗВАНИЕБД')
```

Также установите RabbitMQ и Erlang (всё на офф сайтах https://www.rabbitmq.com/docs/download и 
https://www.erlang.org/downloads)

Затем заходите в терминал и врубаете сначала:

```
python main.py  
```

Затем параллельно:

```
python worker.py   
```

После чего также заходите либо в Swagger на:
```
http://localhost:5000/apidocs
```

Либо же делаете всё вручную через Postman. POST или GET http://localhost:5000/tasks со значениями в Body:

```
{
  "description": "TEST TEST TEST"
}
```