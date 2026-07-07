FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p database app/uploads

EXPOSE 5000

CMD ["gunicorn", "run:app", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120"]
