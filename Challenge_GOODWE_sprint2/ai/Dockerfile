FROM python:3.12-slim
WORKDIR /app
COPY ai/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY ai/ .
ENV AI_HOST=0.0.0.0 AI_PORT=8001
EXPOSE 8001
CMD ["python", "service.py"]
