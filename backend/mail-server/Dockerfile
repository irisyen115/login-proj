FROM python:3.10

WORKDIR /app

COPY mail-server/requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

CMD ["python", "mail_server.py"]
