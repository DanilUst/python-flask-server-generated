# swagger_server/controllers/seller_controller.py
import time
from datetime import datetime

import connexion
from flask import jsonify
from prometheus_client import Counter, Histogram, Gauge  # noqa: F401

from swagger_server.database import db
from swagger_server.logger import logger
from swagger_server.metrics import (
    CARS_ADDED_DETAILED,
    CARS_ADDED_TOTAL,
    CARS_DELETED,
    CARS_IN_DB,
    CARS_UPDATED,
    API_LATENCY
)
from swagger_server.models.seller import seller
from swagger_server.tracer import tracer


user = "admin@example.com"


def seller_controller_create_car(body):  # noqa: E501
    """Создать новую запись."""
    with tracer.start_as_current_span("create_car"):
        start_time = time.time()

        if not connexion.request.is_json:
            return {"message": "Неверный формат запроса"}, 400

        try:
            with tracer.start_as_current_span("parse_json_body"):
                data = connexion.request.get_json()

            with tracer.start_as_current_span("db_insert_car"):
                new_car = seller(
                    name=data.get('name'),
                    content=data.get('content'),
                    price=data.get('price')
                )
                db.session.add(new_car)

            with tracer.start_as_current_span("db_commit"):
                db.session.commit()

            CARS_ADDED_TOTAL.inc()
            CARS_ADDED_DETAILED.labels(car_model=data.get('name')).inc()
            logger.info(
                f"{datetime.now()} Машина создана от пользователя {user}"
            )

            CARS_IN_DB.set(seller.query.count())

            API_LATENCY.labels(
                method='POST',
                endpoint='/seller'
            ).observe(time.time() - start_time)

            return jsonify(new_car.to_dict()), 201

        except Exception as e:
            logger.error(
                f"{datetime.now()} Не удалось создать машину от польз {user}"
            )
            return {"message": str(e)}, 500


def seller_controller_get_cars():
    """Получить все машины."""
    with tracer.start_as_current_span("get_all_cars"):
        start_time = time.time()
        try:
            with tracer.start_as_current_span("db_query_all_cars"):
                cars = seller.query.all()

            API_LATENCY.labels(
                method='GET',
                endpoint='/seller'
            ).observe(time.time() - start_time)

            logger.info(
                f"{datetime.now()} Получена информация о машинах от польз {user}"
            )
            return jsonify([car.to_dict() for car in cars]), 200
        except Exception as e:
            logger.error("Не удалось получить информацию о машинах")
            return {"message": str(e)}, 500


def seller_controller_get_car(car_id):
    """Получить машину по ID."""
    with tracer.start_as_current_span("get_car_by_id"):
        start_time = time.time()
        try:
            with tracer.start_as_current_span("db_query_car"):
                car = seller.query.get(car_id)
                if not car:
                    logger.error(
                        f"{datetime.now()} Не удалось получить информацию "
                        f"о машине с id {car_id} от пользователя {user}"
                    )
                    return {"message": "Машина не найдена"}, 404

            API_LATENCY.labels(
                method='GET',
                endpoint='/seller/{id}'
            ).observe(time.time() - start_time)

            logger.info(
                f"{datetime.now()} Найдена информация о машине с id {car_id} "
                f"от пользователя {user}"
            )
            return jsonify(car.to_dict()), 200
        except Exception as e:
            return {"message": str(e)}, 500


def seller_controller_update_car(body, car_id):
    """Обновить машину."""
    with tracer.start_as_current_span("update_car"):
        start_time = time.time()
        with tracer.start_as_current_span("db_query_car"):
            car = seller.query.get(car_id)
            if not car:
                logger.error(
                    f"{datetime.now()} Не удалось обновить информацию "
                    f"о машине с id {car_id} от пользователя {user}"
                )
                return {"message": "Машина не найдена"}, 404

        if not connexion.request.is_json:
            return {"message": "Неверный формат запроса"}, 400

        try:
            with tracer.start_as_current_span("parse_json_body"):
                data = connexion.request.get_json()

            with tracer.start_as_current_span("update_fields"):
                car.name = data.get('name', car.name)
                car.content = data.get('content', car.content)
                car.price = data.get('price', car.price)

            with tracer.start_as_current_span("db_commit"):
                db.session.commit()

            CARS_UPDATED.inc()

            API_LATENCY.labels(
                method='PUT',
                endpoint='/seller/{id}'
            ).observe(time.time() - start_time)

            logger.info(
                f"{datetime.now()} Обновлена инф-я о машине с id {car_id} "
                f"от пользователя {user}"
            )
            return jsonify(car.to_dict()), 200
        except Exception as e:
            return {"message": str(e)}, 500


def seller_controller_delete_car(car_id):
    """Удалить машину."""
    with tracer.start_as_current_span("delete_car"):
        start_time = time.time()
        with tracer.start_as_current_span("db_query_note"):
            car = seller.query.get(car_id)
            if not car:
                logger.error(
                    f"{datetime.now()} Не удалось удалить информацию "
                    f"о машине с id {car_id} от пользователя {user}"
                )
                return {"message": "Машина не найдена"}, 404

        try:
            with tracer.start_as_current_span("db_delete_car"):
                db.session.delete(car)

            with tracer.start_as_current_span("db_commit"):
                db.session.commit()

            CARS_DELETED.inc()
            CARS_IN_DB.set(seller.query.count())

            API_LATENCY.labels(
                method='DELETE',
                endpoint='/seller/{id}'
            ).observe(time.time() - start_time)

            logger.info(
                f"{datetime.now()} Удалена информация о машине с id {car_id} "
                f"от пользователя {user}"
            )
            return {"message": "Машина удалена"}, 200
        except Exception as e:
            return {"message": str(e)}, 500
