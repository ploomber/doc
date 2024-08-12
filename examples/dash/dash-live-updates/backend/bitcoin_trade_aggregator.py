import asyncio
import json
import asyncpg
import datetime
from websockets import connect
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv(".env")

async def setup_db():
    conn = await asyncpg.connect(user=os.getenv("DB_USER"),
                                password=os.getenv("DB_PASSWORD"),
                                database=os.getenv("DB_NAME"),
                                host=os.getenv("DB_HOST"),
                                port=os.getenv("DB_PORT"))
    await conn.execute("DROP TABLE IF EXISTS trades")
    await conn.execute("""
        CREATE TABLE trades(
            time TIMESTAMPTZ NOT NULL,
            quantity DOUBLE PRECISION,
            price DOUBLE PRECISION
        )
    """)
    await conn.execute("SELECT create_hypertable('trades', 'time')")
    await conn.close()

async def binance(url, db_conn):
    trades_buffer = []
    async with connect(url) as websocket:
        while True:
            data = await websocket.recv()
            data = json.loads(data)
            trades_buffer.append((datetime.datetime.fromtimestamp(data['T']/1000.0), float(data['q']), float(data['p'])))
            # Write in batches of 10
            if len(trades_buffer) > 10:
                await db_conn.executemany("""INSERT INTO trades(time, quantity, price) VALUES ($1, $2, $3)""", trades_buffer)
                trades_buffer = []

async def main():
    url_binance = "wss://data-stream.binance.vision/ws/btcusdt@aggTrade"
    await setup_db()
    db_conn = await asyncpg.connect(user=os.getenv("DB_USER"),
                                    password=os.getenv("DB_PASSWORD"),
                                    database=os.getenv("DB_NAME"),
                                    host=os.getenv("DB_HOST"),
                                    port=os.getenv("DB_PORT"))
    try:
        await binance(url_binance, db_conn)
    finally:
        await db_conn.close()

asyncio.run(main())