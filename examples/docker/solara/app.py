"""# Altair

[Altair](https://altair-viz.github.io/index.html) is a declarative statistical visualization library for Python.

Based on [an Altair example](https://altair-viz.github.io/gallery/annual_weather_heatmap.html)

"""
import altair as alt
from vega_datasets import data
import pandas as pd
import solara
import json

# title = "Altair visualization"
source = data.movies()

selected_datum = solara.reactive(None)


@solara.component
def Page():
    def on_click(datum):
        selected_datum.value = datum

    pts = alt.selection_point(encodings=['x'])

    rect = alt.Chart(data.movies.url).mark_rect().encode(
        alt.X('IMDB_Rating:Q').bin(),
        alt.Y('Rotten_Tomatoes_Rating:Q').bin(),
        alt.Color('count()').scale(scheme='greenblue').title('Total Records')
    )

    circ = rect.mark_point().encode(
        alt.ColorValue('grey'),
        alt.Size('count()').title('Records in Selection')
    ).transform_filter(
        pts
    )

    bar = alt.Chart(source, width=550, height=200).mark_bar().encode(
        x='Major_Genre:N',
        y='count()',
        color=alt.condition(pts, alt.ColorValue("steelblue"), alt.ColorValue("grey"))
    ).add_params(pts)

    alt.vconcat(
        rect + circ,
        bar
    ).resolve_legend(
        color="independent",
        size="independent"
    )

    with solara.Card("Interactive Chart"):
        solara.Markdown("This dashboard uses [Solara](https://github.com/widgetti/solara) to display an interactive chart where selections in one portion of the chart affect what is shown in the other panel.")
        solara.Markdown("Data: Vega [movies](https://github.com/vega/vega/blob/main/docs/data/movies.json) dataset. It contains information about movies, such as their titles, release years, genre, IMDB rating, Rotten tomatoes rating etc.")
        solara.Markdown("Hosted in [Ploomber Cloud](https://ploomber.io/)")
        solara.Markdown("How to use it: Click on the bar chart to see a detail of the distribution in the upper panel. It will also display the data for the selected genre in a table below.")
        solara.Markdown("##Visualisations")
        solara.Markdown("* **Correlation chart**: The first chart is a visualization that allows you to explore the relationship between movie ratings on Rotten Tomatoes and IMDb. It's designed to provide insights into how these two different rating systems correlate and whether there are any noticeable patterns or trends in movie ratings. The X-axis represents the IMDb ratings of movies. IMDb ratings are typically on a scale of 1 to 10, with 10 being the highest rating. This axis is divided into bins, which group movies by their IMDb ratings. The Y-axis represents the Rotten Tomatoes ratings of movies. Rotten Tomatoes ratings are often represented as percentages, indicating the percentage of critics or audience members who rated a movie positively. The color of each bin in the chart is used to indicate the number of movies falling within that rating range. Lighter colors represent fewer movies and darker colors represent more movies.")
        solara.Markdown("* **Bar chart**: This indicates how many data points or items fall under each genre category.")
        solara.AltairChart(rect)
        solara.AltairChart(bar, on_click=on_click)
        df = source
        if selected_datum.value:
            genre = selected_datum.value["Major_Genre"]
            genre_df = df[df["Major_Genre"] == genre]
            solara.Button("Clear selection", on_click=lambda: selected_datum.set(None))
            #solara.display(
            solara.DataFrame(genre_df, scrollable=True)

            with solara.Details("Click data"):
                solara.Markdown(
                    f"""
                Click data:

                ```
                {selected_datum.value}
                ```
                """
                )
        else:
            solara.Markdown("Click on the bar chart to see data for a specific genre")