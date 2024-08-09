import numpy as np
import pandas as pd
import panel as pn

import holoviews as hv
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

DB_URI = "postgresql://demo_owner:vnpjXDHdM16C@ep-lively-union-a5gh7z48.us-east-2.aws.neon.tech/demo?sslmode=require"

engine = create_engine(DB_URI, pool_pre_ping=True)

metadata = MetaData()
metadata.reflect(bind=engine)
table_names = [table.name for table in metadata.tables.values()]

table = pn.widgets.Select(name='Select Table', options=table_names)

limit = pn.widgets.IntSlider(name='Limit Rows', start=0, end=1500)

def get_data(engine, table, limit):
    with engine.connect() as conn:
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

def getQuantVars(wine_data):
    return wine_data.select_dtypes('number').columns.to_list()

wine_data = pn.bind(get_data, engine=engine, table=table, limit=limit)

quant_vars = pn.bind(getQuantVars, wine_data=wine_data)

hist_var = pn.widgets.Select(name = "Histogram Variable", options=quant_vars)

scatter_x = pn.widgets.Select(name = "Scatterplot X", options=quant_vars)

scatter_y = pn.widgets.Select(name = "Scatterplot Y", options=quant_vars)

scatter = pn.bind(plotScatter, wine_data=wine_data, x=scatter_x, y=scatter_y)

hist = pn.bind(plotHist, wine_data=wine_data, hist_var=hist_var)


# histogram = wine_data.hvplot.hist(
#     "body_mass_g",
#     by="species",
#     color=hv.dim("species").categorize(colors),
#     legend=False,
#     alpha=0.5,
#     responsive=True,
#     min_height=300,
# )

# bars = penguins.hvplot.bar(
#     "species",
#     "index",
#     c="species",
#     cmap=colors,
#     responsive=True,
#     min_height=300,
#     ylabel="",
# ).aggregate(function=np.count_nonzero)

# violin = penguins.hvplot.violin(
#     "flipper_length_mm",
#     by=["species", "sex"],
#     cmap="Category20",
#     responsive=True,
#     min_height=300,
#     legend="bottom_right",
# ).opts(split="sex")


# plots = pn.pane.HoloViews(
#     scatter
# ).servable(title="Wine Quality", target="main")
scatterWidget = pn.WidgetBox('# Select Variables', scatter_x, scatter_y, max_width=350)
row1= pn.Column(pn.Row(scatterWidget, scatter, sizing_mode="stretch_both"))
row2= pn.Column(hist, hist_var, sizing_mode="stretch_both")

template = pn.template.FastListTemplate(title="Wine Quality - PostgreSQL + Panel Ploomber Demo", main= [row1, row2],sidebar=[table, limit], sidebar_width=280)



template.servable()

