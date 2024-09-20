FROM python:3.9.20-alpine

WORKDIR /access_manager

COPY . .

RUN pip install -r requirements.txt

EXPOSE 80

CMD ["sh", "-c", "python3 app.py"]
