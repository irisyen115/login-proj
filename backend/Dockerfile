FROM python:3.9

WORKDIR /app

COPY . .

RUN pip install --no-cache-dir flask psycopg2 flask-bcrypt flask-cors

CMD ["python", "app.py"]
