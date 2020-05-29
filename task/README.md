Install requirements:

`pip install -r requirements.txt`

Run RabbitMQ:

`docker-compose up rabbitmq`

Run worker:

`celery -A task worker --loglevel=info`

Run beat:

`celery -A task beat --loglevel=info`
