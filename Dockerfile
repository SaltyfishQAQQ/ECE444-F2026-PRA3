FROM python:3.9

WORKDIR /app

COPY requirements.txt .
RUN python3 -m pip install -r requirements.txt

COPY hello.py .
COPY templates templates

EXPOSE 5000

CMD ["python3", "-m", "flask", "--app", "hello", "run", "--host=0.0.0.0"]
