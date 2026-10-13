# Yengil Python muhiti
FROM python:3.11-slim

# Ishchi katalog
WORKDIR /app

# Bog'liqliklarni nusxalash va o'rnatish
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Loyiha fayllarini nusxalash
COPY . .

# Portni ochish
EXPOSE 5000

# Dasturni ishga tushirish
CMD ["python", "app.py"]
