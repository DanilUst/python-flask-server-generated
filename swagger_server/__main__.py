#!/usr/bin/env python3

import connexion
import logging
import os
from logging.handlers import RotatingFileHandler

from prometheus_client import make_wsgi_app
from werkzeug.middleware.dispatcher import DispatcherMiddleware

from swagger_server import encoder
from swagger_server.database import db
from swagger_server.logger import logger
from swagger_server.tracer import configure_tracing


def setup_logging(app):
    """Настройка логирования с ротацией и структурным форматом."""
    # Создаем директорию для логов, если её нет
    log_dir = '/var/log/flask-api'
    os.makedirs(log_dir, exist_ok=True)
    
    # Формат логов (структурированный JSON)
    formatter = logging.Formatter(
        '{"time": "%(asctime)s", "level": "%(levelname)s", "module": "%(module)s", '
        '"message": "%(message)s", "endpoint": "%(pathname)s:%(lineno)d"}'
    )

    # Ротация логов (10 MB, 5 файлов)
    file_handler = RotatingFileHandler(
        f'{log_dir}/app.log',
        maxBytes=10*1024*1024,
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    file_handler.setLevel(logging.INFO)

    # Вывод в консоль
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.DEBUG)

    # Применяем обработчики
    app.app.logger.addHandler(file_handler)
    app.app.logger.addHandler(console_handler)
    app.app.logger.setLevel(logging.INFO)

    # Логирование запросов (access log)
    werkzeug_logger = logging.getLogger('werkzeug')
    werkzeug_logger.addHandler(file_handler)
    werkzeug_logger.addHandler(console_handler)


def main():
    # Инициализация Connexion приложения
    app = connexion.App(__name__, specification_dir='./swagger/')
    
    # Настройка логирования
    # setup_logging(app)
    
    # Совместимость с Flask 2.3+
    if hasattr(app.app, 'json_provider_class'):
        app.app.json_provider_class = encoder.JSONEncoder
    else:
        app.app.json_encoder = encoder.JSONEncoder
    
    # Добавление Swagger API
    app.add_api(
        'swagger.yaml',
        arguments={'title': 'Cars Seller'},
        pythonic_params=True
    )
    
    # Настройка Prometheus метрик
    app.app.wsgi_app = DispatcherMiddleware(
        app.app.wsgi_app,
        {'/metrics': make_wsgi_app()}
    )
    
    # Конфигурация базы данных
    app.app.config['SQLALCHEMY_DATABASE_URI'] = \
        'sqlite:////usr/src/app/seller.db'
    app.app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    db.init_app(app.app)
    
    # Создание таблиц
    with app.app.app_context():
        db.create_all()
    
    # Стартовая запись в лог
    logger.info("Server started")
    configure_tracing(app)
    # Запуск приложения
    app.run(host='0.0.0.0', port=8080)


if __name__ == '__main__':
    main()