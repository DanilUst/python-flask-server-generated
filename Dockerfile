FROM python:3.8-slim

WORKDIR /usr/src/app

# Сначала копируем только requirements.txt для кэширования
COPY requirements.txt .

# Устанавливаем системные зависимости для SQLAlchemy
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc python3-dev && \
    rm -rf /var/lib/apt/lists/*

# Устанавливаем Python-зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Копируем остальные файлы
COPY . .

EXPOSE 8080

CMD ["python", "-m", "swagger_server"]
# Добавьте эту строку для сохранения БД между перезапусками
VOLUME /usr/src/app