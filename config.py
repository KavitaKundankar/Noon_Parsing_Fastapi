# Configuration for RabbitMQ and Daily Limits

QUEUE_NAME = "NOON_PARSER_DATA_QUEUE"
DAILY_LIMIT = 4

RABBIT_CFG = {
    "host": "localhost",
    "port": 5672,
    "vhost": "myvhost",
    "username": "user",
    "password": "password"
}

REDIS_CFG = {
    "host": "localhost",
    "port": 9226,
    "username": "sshuser",
    "password": "adminssh",
    "db": 0
}
