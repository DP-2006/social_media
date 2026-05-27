FROM python:3.11-slim

WORKDIR /app

# کپی requirements و نصب پکیج‌ها
COPY requirements.txt .
RUN pip install --no-cache-dir --default-timeout=100 -r requirements.txt

# کپی کل پروژه
COPY . .

# پورت
EXPOSE 8000

# اجرا
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
