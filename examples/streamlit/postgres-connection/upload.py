from sqlalchemy import create_engine
from ucimlrepo import fetch_ucirepo
import pandas as pd


DB_URI = "postgresql://demo_owner:7iAYbGmr8eOJ@ep-lively-credit-a52udj7x.us-east-2.aws.neon.tech/demo?sslmode=require"
# url=environ["DB_URI"]

# Loading in iris dataset
iris = fetch_ucirepo(name="Iris")
iris_df = iris.data.original
iris_df.reset_index(drop=True)

# Create the SQL connection to the numbers DB as specified in your secret.

engine = create_engine(DB_URI)
with engine.connect() as engine_conn:
    iris_df.to_sql(name="iris", con=engine_conn, if_exists='replace', index=False)
    print("Data successfully uploaded.")
engine.dispose()
