FROM python:3.11-slim

WORKDIR /app

# install runtime dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# copy app
COPY . /app

EXPOSE 8000

# Default env variables for microservice endpoints (can be overridden at runtime)
ENV ADD_SERVICE_URL="http://add-service:8000/add"
ENV SUB_SERVICE_URL="http://sub-service:8000/sub"
ENV MUL_SERVICE_URL="http://mul-service:8000/mul"
ENV DIV_SERVICE_URL="http://div-service:8000/div"

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
