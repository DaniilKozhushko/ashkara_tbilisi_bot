FROM python:3.11-slim

# установка рабочей директории
WORKDIR /app

# копирование requirements
COPY requirements.txt .

# установка зависимостей python
RUN pip install --no-cache-dir -r requirements.txt

# копирование всего остального
COPY . .

# запуск бота
CMD ["python", "main.py"]