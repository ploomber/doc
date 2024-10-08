import numpy as np
import pandas as pd
import panel as pn

import holoviews as hv
import hvplot.pandas  # noqa
from sqlalchemy import text, create_engine, MetaData
from os import environ
from ucimlrepo import fetch_ucirepo

pn.extension(sizing_mode="stretch_width")

# Updates iris table with the original dataset
def upload_data(DB_URI):
    # Loading in iris dataset
    wine = fetch_ucirepo(name="Wine Quality")
    wine_df = wine.data.original
    wine_df.reset_index(drop=True)

    red = wine_df[wine_df["color"] == "red"]
    white = wine_df[wine_df["color"] == "white"] 

    engine = create_engine(DB_URI, pool_pre_ping=True)
    with engine.connect() as engine_conn:
        red.to_sql(name="red_wine", con=engine_conn, if_exists='replace', index=False)
        white.to_sql(name="white_wine", con=engine_conn, if_exists='replace', index=False)
        print("Data successfully uploaded.")
    engine.dispose()

DB_URI = "YOUR DB_URI"

# IF you are deploying with Ploomber Cloud, set DB_URI = environ["DB_URI"] instead
# DB_URI = environ["DB_URI"]

engine = create_engine(DB_URI, pool_pre_ping=True)

metadata = MetaData()
metadata.reflect(bind=engine)
table_names = [table.name for table in metadata.tables.values()]

table = pn.widgets.Select(name='Select Table', options=table_names)

limit = pn.widgets.IntSlider(name='Limit Rows (If 0, shows all)', start=0, end=1500)

def get_data(engine, table, limit):
    with engine.connect() as conn:
        if limit == 0: 
            wine_data = pd.read_sql(sql=f"SELECT * FROM {table}", con=conn)
        else: 
            wine_data = pd.read_sql(sql=f"SELECT * FROM {table} LIMIT {limit}", con=conn)
    conn.close()
    return wine_data

def plotScatter(wine_data, x, y):
    scatter = wine_data.hvplot.points(
        x,
        y,
        color=wine_data["color"].replace({"white":"black"}),
        responsive=True,
        min_height=270,
    )
    return scatter

def plotHist(wine_data, hist_var):
    hist = wine_data.hvplot.hist(
        hist_var, 
        min_height=270,
        responsive=True
    )
    return hist

def getAvg(wine_data, var):
    avg = wine_data[var].mean()
    return pn.indicators.Number(name = "Average Quality Score", value=round(avg, 2))

def getQuantVars(wine_data):
    return wine_data.select_dtypes('number').columns.to_list()

wine_data = pn.bind(get_data, engine=engine, table=table, limit=limit)

qualityScore = pn.bind(getAvg, wine_data=wine_data, var="quality")

quant_vars = pn.bind(getQuantVars, wine_data=wine_data)

hist_var = pn.widgets.Select(name = "Histogram Variable", options=quant_vars)

scatter_x = pn.widgets.Select(name = "Scatterplot X", options=quant_vars)

scatter_y = pn.widgets.Select(name = "Scatterplot Y", options=quant_vars)

scatter = pn.bind(plotScatter, wine_data=wine_data, x=scatter_x, y=scatter_y)

hist = pn.bind(plotHist, wine_data=wine_data, hist_var=hist_var)

scatterWidget = pn.WidgetBox('# Select Variables', scatter_x, scatter_y, max_width=350)
row1= pn.Column(pn.Row(scatterWidget, scatter, sizing_mode="stretch_both"))
row2= pn.Column(hist, hist_var, sizing_mode="stretch_both")

template = pn.template.FastListTemplate(title="Wine Quality - PostgreSQL + Panel Ploomber Demo", main= [row1, row2],sidebar=[table, limit, qualityScore], sidebar_width=280)

template.servable()

