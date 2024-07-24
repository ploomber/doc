import streamlit as st
from sqlalchemy import text, create_engine
from os import environ
import pandas as pd
from ucimlrepo import fetch_ucirepo
import psycopg2


# Create the SQL connection to the numbers DB as specified in your secret.

# Updates iris table with original
def upload_data(DB_URI):
    # Loading in iris dataset
    iris = fetch_ucirepo(name="Iris")
    iris_df = iris.data.original
    iris_df.reset_index(drop=True)

    engine = create_engine(DB_URI)
    with engine.connect() as engine_conn:
        iris_df.to_sql(name="iris", con=engine_conn, if_exists='replace', index=False)
        print("Data successfully uploaded.")
    engine.dispose()


DB_URI = "postgresql://demo_owner:7iAYbGmr8eOJ@ep-lively-credit-a52udj7x.us-east-2.aws.neon.tech/demo?sslmode=require"
# url=environ["DB_URI"]

conn_st = st.connection(name="postgres", type='sql', url=DB_URI)

st.title("Streamlit with Postgres Demo")
iris_data = conn_st.query("SELECT * FROM iris")

with st.sidebar:    
    reset = st.button("Reset Data")
    st.header("Add Iris Data")
    st.subheader("After submitting, a new row with the data will be added to the 'iris' table in our database.")
    with st.form(key='new_data'):
        sepal_length = st.text_input(label="Sepal Length", key=1)
        sepal_width = st.text_input(label="Sepal Length", key=2)
        petal_length = st.text_input(label="Petal Length", key=3)
        petal_width = st.text_input(label="Petal Width", key=4)
        iris_class = st.selectbox(label="Iris Class", key=5, options=iris_data["class"].unique())
        submit = st.form_submit_button('Add')

if reset:
    upload_data(DB_URI)
    st.cache_data.clear()
    iris_data = conn_st.query("SELECT * FROM iris")

if submit:
    with conn_st.session as s:
        new_data = (sepal_length, sepal_width, petal_length, petal_width, iris_class)
        q = """
                INSERT INTO iris ("sepal length", "sepal width", "petal length", "petal width", "class")
                VALUES (:sepal_length, :sepal_width, :petal_length, :petal_width, :iris_class)
            """
        s.execute(text(q), {
            'sepal_length': sepal_length,
            'sepal_width': sepal_width,
            'petal_length': petal_length,
            'petal_width': petal_width,
            'iris_class': iris_class
        })
        s.commit()
    st.cache_data.clear()
    iris_data = conn_st.query("SELECT * FROM iris")

col1, col2 = st.columns(2)

with col1:
    st.metric("Average Sepal Length", round(iris_data["sepal length"].mean(), 2))
with col2:
    st.metric("Average Sepal Width", round(iris_data["sepal width"].mean(), 2))
with col1:
    st.metric("Average Petal Length", round(iris_data["petal length"].mean(), 2))
with col2:
    st.metric("Average Petal Width", round(iris_data["petal width"].mean(), 2))

st.divider()
# Scatter plot selector
st.header("Scatter Plot")
with col1: 
    x = st.selectbox("Select X-Variable", options=iris_data.select_dtypes("number").columns, index=0)
with col2:
    y = st.selectbox("Select Y-Variable", options=iris_data.select_dtypes("number").columns, index=1)

# Scatter plot

scatter_chart = st.scatter_chart(iris_data, x=x, y=y, size=40, color='class',)

st.divider()

st.dataframe(iris_data)
