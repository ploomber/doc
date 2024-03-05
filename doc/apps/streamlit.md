# Streamlit

Ploomber Cloud supports [Streamlit](https://streamlit.io/). For information on how to develop Streamlit apps, [please check the documentation](https://docs.streamlit.io/).

To deploy a Streamlit app you need at least two files:

1. Your application file (`app.py`)
2. A dependencies file (`requirements.txt`)

## Application file

Your `app.py` must be a Streamlit application. An example is available [here.](https://github.com/ploomber/doc/blob/main/examples/streamlit/data-viz/app.py)

## Dependencies

To deploy a new project, list your dependencies in a (`requirements.txt`). You must include the streamlit package. If you're using pandas and numpy together, your `requirements.txt` file will look like this:

```
# sample requirements.txt
streamlit
pandas
numpy
```

## Testing locally

To test your Streamlit app, you can run the following command locally:

```bash
streamlit run app.py
```

## Deploy

To deploy a Streamlit app from the deployment menu, follow these instructions:

![](../static/streamlit.png)
