import asyncio, asyncpg, datetime, json, os
from websockets import connect
from dotenv import load_dotenv

# Load environment variables
load_dotenv(".env")

async def setup_db():
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    db_host = os.getenv('DB_HOST')
    db_port = os.getenv('DB_PORT')
    db_name = os.getenv('DB_NAME')

    if not all([db_user, db_password, db_host, db_port, db_name]):
        raise ValueError("Database connection details are not fully set in environment variables")

    conn = await asyncpg.connect(user=db_user,
                                password=db_password,
                                database=db_name,
                                host=db_host,
                                port=db_port)
    await conn.execute("DROP TABLE IF EXISTS trades")
    await conn.execute("""
        CREATE TABLE trades(
            time TIMESTAMP NOT NULL,
            price DOUBLE PRECISION
        )
    """)
    await conn.execute("SELECT create_hypertable('trades', 'time')")
    await conn.close()


async def insert_data(url, db_conn):
    trades_buffer = []
    async with connect(url) as websocket:
        while True:
            data = await websocket.recv()
            data = json.loads(data)
            trades_buffer.append((datetime.datetime.fromtimestamp(data['T']/1000.0), float(data['p'])))
            print(trades_buffer[-1])
            # Write in batches of 5
            if len(trades_buffer) > 5:
                await db_conn.executemany("""INSERT INTO trades(time, price) VALUES ($1, $2)""", trades_buffer)
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
        await insert_data(url_binance, db_conn)
    finally:
        await db_conn.close()

if __name__ == "__main__":
    asyncio.run(main())