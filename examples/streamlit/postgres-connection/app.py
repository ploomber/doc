import streamlit as st
from sqlalchemy import text
from os import environ
import pandas as pd
import psycopg2

DB_URI = "postgresql://demo_owner:7iAYbGmr8eOJ@ep-lively-credit-a52udj7x.us-east-2.aws.neon.tech/demo?sslmode=require"
# url=environ["DB_URI"]

conn_st = st.connection(name="postgres", type='sql', url=DB_URI)

st.title("Streamlit with Postgres Demo")
iris_data = conn_st.query("SELECT * FROM iris")

with st.sidebar:    
    st.header("Add Iris Data")
    with st.form(key='new_data'):
        sepal_length = st.text_input(label="Sepal Length", key=1)
        sepal_width = st.text_input(label="Sepal Length", key=2)
        petal_length = st.text_input(label="Petal Length", key=3)
        petal_width = st.text_input(label="Petal Width", key=4)
        iris_class = st.selectbox(label="Iris Class", key=5, options=iris_data["class"].unique())
        submit = st.form_submit_button('Add')


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


st.metric("Average Sepal Length", round(iris_data["sepal length"].mean(), 2))
st.metric("Average Sepal Width", round(iris_data["sepal width"].mean(), 2))
st.metric("Average Petal Length", round(iris_data["petal length"].mean(), 2))
st.metric("Average Petal Width", round(iris_data["petal width"].mean(), 2))
st.dataframe(iris_data)
