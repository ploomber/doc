import solara
import plotly.express as px
from solara.lab import headers

df = px.data.iris()

columns = list(df.columns)
x_axis = solara.reactive("sepal_length")
y_axis = solara.reactive("sepal_width")


@solara.component
def Page():
    if 'x-auth-name' in headers.value:
        username = headers.value['x-auth-name'][0]
    else:
        username = "Anonymous"
    solara.Markdown(f"Welcome {username}!")
    solara.Markdown("[Logout](/logout)")

    fig = px.scatter(df, x_axis.value, y_axis.value)
    solara.FigurePlotly(fig)
    solara.Select(label="X-axis", value=x_axis, values=columns)
    solara.Select(label="Y-axis", value=y_axis, values=columns)
