# Data querying and visualisation App

This query and data visualisation application is designed to provide a user-friendly chatbot interface to interact with your data, making data exploration and analysis a breeze.


## Getting Started

To get started with this app, follow these steps:

1. Login to your [Ploomber Cloud](https://ploomber.io/) account.

2. Follow the [steps](https://docs.cloud.ploomber.io/en/latest/apps/solara.html) for deploying a Solara application and upload the `app.zip` file provided in the example. Ensure to add your own `openai` API Key in `app.py` file.

## How to use

1. **Dataset**: Click the `SAMPLE DATASET` button to load a sample csv file, or upload your own content by dragging a file to the drop area. You may also clear the loaded data by clicking the `Clear Dataset` button.

2. **Number of preview rows**: Input the desired number of preview rows to be displayed.

3. **Interaction**: You may ask the chatbot natural language queries like : `top 20 rows of table`, `unique values of column with counts`, etc.

4. **Data visualisation**: Visualize your data on the fly. Currently, the app supports histogram and box plot on a specific column, e.g., `histogram on column`.

5. **Export Results**: The app allows you to export the charts, or query results.