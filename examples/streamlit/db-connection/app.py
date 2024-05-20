import streamlit as st
from sqlalchemy.sql import text
from os import environ

# Create the SQL connection to the numbers DB as specified in your secret.
conn = st.connection(name="sqlite", type='sql', url=environ["DB_URI"])

# Insert some data with conn.session.
with conn.session as s:
    s.execute(text('CREATE TABLE IF NOT EXISTS numbers (x INT, y INT);'))
    s.execute(text('DELETE FROM numbers;'))
    num_pairs = {'1': '1', '2': '4', '3': '9'}
    for k in num_pairs:
        s.execute(
            text('INSERT INTO numbers (x, y) VALUES (:numx, :numy);'),
            params=dict(numx=k, numy=num_pairs[k])
        )
    s.commit()

# Query and display the data you inserted
numbers = conn.query('select * from numbers')
st.dataframe(numbers)
