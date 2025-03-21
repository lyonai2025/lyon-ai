# casino_app/Dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_APP=main.py
ENV FLASK_DEBUG=False

EXPOSE 5000

CMD ["gunicorn", "--bind", "0.0.0.0:5000", "main:app"]
