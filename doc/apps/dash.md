# Dash

To deploy a [Dash](https://dash.plotly.com/) application to Ploomber Cloud you need at least two files zipped up:

1. Your application file (`app.py`)
2. A dependencies file (`requirements.txt`)

## Required files

You can use this [template](https://github.com/ploomber/doc/blob/main/examples/dash) to get started. 

In the `requirements.txt` file, add all the dependencies that you need for your application to run. The application logic should exist in an `app.py` file and be initialized in this way:

```python
# name your app "app"
app = Dash(__name__)
# add this line below
server = app.server
```

## Testing locally

To test the Dash application, you can run the following commands locally:

```sh
# build the docker image
pip install -r requirements.txt

# Start the dash application
gunicorn app:server run --bind 0.0.0.0:5000
```

Now, open [http://0.0.0.0:5000/](http://0.0.0.0:5000/) to see your app.


## Deploy

Once you have all your files, create a zip file.

To deploy a Dash app from the deployment menu, select the Dash option and follow the instructions:

![](../static/dash.png)