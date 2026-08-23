FROM python:3.11-slim

WORKDIR /app

# Свежий pip лучше разруливает зависимости
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p data logs

CMD ["python", "main.py"]
