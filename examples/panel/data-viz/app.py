import numpy as np
import pandas as pd
import panel as pn

import holoviews as hv
import hvplot.pandas  # noqa

pn.extension(template="fast")

pn.state.template.logo = (
    "https://github.com/allisonhorst/palmerpenguins/raw/main/man/figures/logo.png"
)

welcome = "## Welcome and meet the Palmer penguins!"

penguins_art = pn.pane.PNG(
    "https://raw.githubusercontent.com/allisonhorst/palmerpenguins/main/man/figures/palmerpenguins.png",
    height=160,
)

credit = "### Artwork by @allison_horst"

instructions = """
Use the box-select and lasso-select tools to select a subset of penguins
and reveal more information about the selected subgroup through the power
of cross-filtering.
"""

license = """
### License

Data are available by CC-0 license in accordance with the Palmer Station LTER Data Policy and the LTER Data Access Policy for Type I data."
"""

art = pn.Column(
    welcome, penguins_art, credit, instructions, license, sizing_mode="stretch_width"
).servable(area="sidebar")

art


penguins = pd.read_csv("https://datasets.holoviz.org/penguins/v1/penguins.csv")
penguins = penguins[~penguins.sex.isnull()].reset_index().sort_values("species")

penguins

ls = hv.link_selections.instance()


def count(selected):
    return f"## {len(selected)}/{len(penguins)} penguins selected"


selected = pn.pane.Markdown(
    pn.bind(count, ls.selection_param(penguins)),
    align="center",
    width=400,
    margin=(0, 100, 0, 0),
)

header = pn.Row(pn.layout.HSpacer(), selected, sizing_mode="stretch_width").servable(
    area="header"
)

selected

colors = {"Adelie": "#1f77b4", "Gentoo": "#ff7f0e", "Chinstrap": "#2ca02c"}

scatter = penguins.hvplot.points(
    "bill_length_mm",
    "bill_depth_mm",
    c="species",
    cmap=colors,
    responsive=True,
    min_height=300,
)

histogram = penguins.hvplot.hist(
    "body_mass_g",
    by="species",
    color=hv.dim("species").categorize(colors),
    legend=False,
    alpha=0.5,
    responsive=True,
    min_height=300,
)

bars = penguins.hvplot.bar(
    "species",
    "index",
    c="species",
    cmap=colors,
    responsive=True,
    min_height=300,
    ylabel="",
).aggregate(function=np.count_nonzero)

violin = penguins.hvplot.violin(
    "flipper_length_mm",
    by=["species", "sex"],
    cmap="Category20",
    responsive=True,
    min_height=300,
    legend="bottom_right",
).opts(split="sex")

plots = pn.pane.HoloViews(
    ls(scatter.opts(show_legend=False) + bars + histogram + violin)
    .opts(sizing_mode="stretch_both")
    .cols(2)
).servable(title="Palmer Penguins")

plots
