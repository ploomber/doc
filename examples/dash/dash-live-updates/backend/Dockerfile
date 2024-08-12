FROM python:3.9-slim

WORKDIR /app

COPY . .

# Install dependencies
RUN pip install asyncpg websockets python-dotenv

# Command to run the backend
CMD ["python", "bitcoin_trade_aggregator.py"]