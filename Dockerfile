# comp-calc/Dockerfile
FROM python:3.11.4-slim

WORKDIR /app

COPY . .

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 5001

CMD ["python", "app.py"]
