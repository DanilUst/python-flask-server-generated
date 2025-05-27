# swagger_server/controllers/seller_controller.py
import connexion
from flask import jsonify
from swagger_server.database import db
from swagger_server.models.seller import seller
from prometheus_client import Counter, Histogram, Gauge
import time
from datetime import datetime
from swagger_server.logger import logger
from swagger_server.tracer import tracer
from swagger_server.metrics import CARS_ADDED_DETAILED, CARS_DELETED, CARS_UPDATED, CARS_IN_DB, API_LATENCY, CARS_ADDED_TOTAL


user = "admin@example.com"

def seller_controller_create_car(body):
    """Создать новую запись"""
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
                
                # Определяем ценовой диапазон для метрики
                price = data.get('price', 0)
                price_range = f"{price//10000 * 10000}-{(price//10000 + 1) * 10000}"
                
                CARS_ADDED_TOTAL.inc()
                CARS_ADDED_DETAILED.labels(car_model=data.get('name')).inc()
                logger.info(str(datetime.now()) + " Машина создана"   + " от пользователя " + user)

                # Обновляем количество машин в БД
                CARS_IN_DB.set(seller.query.count())
                
                # Фиксируем время выполнения
                API_LATENCY.labels(
                    method='POST',
                    endpoint='/seller'
                ).observe(time.time() - start_time)
                
                return jsonify(new_car.to_dict()), 201
            
        except Exception as e:
            logger.error(str(datetime.now()) + " Не удалось создать машину"  + " от пользователя " + user)
            return {"message": str(e)}, 500
        

def seller_controller_get_cars():
    """Получить все машины"""
    with tracer.start_as_current_span("get_all_cars"):
        start_time = time.time()
        try:
            with tracer.start_as_current_span("db_query_all_cars"):
                cars = seller.query.all()
                # Фиксируем время выполнения
                API_LATENCY.labels(
                    method='GET',
                    endpoint='/seller'
                ).observe(time.time() - start_time)
                logger.info(str(datetime.now()) + " Получены вся информация о машинах "  + " от пользователя " + user)
                return jsonify([car.to_dict() for car in cars]), 200
        except Exception as e:
            logger.error("Не удалось получить информацию о машинах")
            return {"message": str(e)}, 500

def seller_controller_get_car(car_id):
    """Получить машину по ID"""

    with tracer.start_as_current_span("get_car_by_id"):
        start_time = time.time()
        try:
            with tracer.start_as_current_span("db_query_car"):
                car = seller.query.get(car_id)
                if not car:
                    logger.error(str(datetime.now())  +  " Не удалось получить информацию о машине с id " + str(car_id) + " от пользователя " + user)
                    return {"message": "Машина не найдена"}, 404
                    
                # Фиксируем время выполнения
                API_LATENCY.labels(
                    method='GET',
                    endpoint='/seller/{id}'
                ).observe(time.time() - start_time)
                logger.info(str(datetime.now())  +  " Найдена информация о машину с id " + str(car_id) + " от пользователя " + user)
                return jsonify(car.to_dict()), 200
        except Exception as e:
            return {"message": str(e)}, 500

def seller_controller_update_car(body, car_id):
    """Обновить машину"""

    with tracer.start_as_current_span("update_car"):
        start_time = time.time()
        with tracer.start_as_current_span("db_query_car"):
            car = seller.query.get(car_id)
            if not car:
                logger.error(str(datetime.now())  + " Не удалось обновить информацию о машине с id " + str(car_id) + " от пользователя " + user)
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
                
                # Увеличиваем счетчик обновлений
                CARS_UPDATED.inc()
                
                # Фиксируем время выполнения
                API_LATENCY.labels(
                    method='PUT',
                    endpoint='/seller/{id}'
                ).observe(time.time() - start_time)
                logger.info(str(datetime.now())  + " Обновлена информация о машине с id " + str(car_id) + " от пользователя " + user)
                return jsonify(car.to_dict()), 200
            except Exception as e:
                return {"message": str(e)}, 500

def seller_controller_delete_car(car_id):
    """Удалить машину"""
    with tracer.start_as_current_span("delete_car"):
        start_time = time.time()
        with tracer.start_as_current_span("db_query_note"):
            car = seller.query.get(car_id)
            if not car:
                logger.error(str(datetime.now()) + " Не удалось удалить информацию о машине с id " + str(car_id) +  " от пользователя " + user)
                return {"message": "Машина не найдена"}, 404
            
        try:
            with tracer.start_as_current_span("db_delete_car"):
                db.session.delete(car)
            with tracer.start_as_current_span("db_commit"):
                db.session.commit()
            
            # Увеличиваем счетчик удалений
            CARS_DELETED.inc()
            
            # Обновляем количество машин в БД
            CARS_IN_DB.set(seller.query.count())
            
            # Фиксируем время выполнения
            API_LATENCY.labels(
                method='DELETE',
                endpoint='/seller/{id}'
            ).observe(time.time() - start_time)
            logger.info(str(datetime.now())  + " Удалена информация о машине с id " + str(car_id) +  " от пользователя " + user)
            return {"message": "Машина удалена"}, 200
        except Exception as e:
            return {"message": str(e)}, 500