FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install --no-cache-dir ".[enterprise]"
EXPOSE 8000
CMD ["python", "-m", "synergy_relative_value.api"]
