# استفاده از تصویر پایتون به عنوان پایه
FROM python:3.9-slim

# نصب وابستگی‌ها
RUN pip install requests

# تنظیم مسیر کاری
WORKDIR /app

COPY network_check.py .

# اجرای اسکریپت
CMD ["python", "network_check.py"]
