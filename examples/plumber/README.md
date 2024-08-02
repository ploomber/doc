# REST API with Plumber 

A RESTful API built with the Plumber package in R.
The API provides three main functions:
- Checking the server status of the API with a GET request.
- Predicting iris petal length based on various parameters with a POST request.
- Displaying a plot that compares actual to predicted petal lengths with a GET request.

## Steps for Testing Locally

To run the API locally, use the following command in your terminal:
```sh
Rscript main.R
```

Now you can explore your Swagger Docs at `http://127.0.0.1/__docs__/`.

### Health Check (GET)
Check the API's server status with:
```sh
curl -X 'GET' 'http://127.0.0.1/health_check'
```

### Predict Petal Length (POST)

To predict petal length with only the petal width:
```sh
curl -X 'POST' 'http://127.0.0.1/predict_petal_length' -d 'petal_width=10'
```

To include petal width, sepal length, sepal width, and species of the flower:
```sh
curl -X 'POST' 'http://127.0.0.1/predict_petal_length' -d "petal_width=1.2" -d "sepal_length=3.5" -d "sepal_width=2.1" -d "species=setosa"
```

### Plot Actual vs Predicted (GET)
To download a plot comparing actual and predicted petal lengths:
```sh
curl -X 'GET' 'http://127.0.0.1/plot_actual_vs_predicted' --output plot.png
```

## Steps for Deploying on Ploomber Cloud
### Prerequisites
- [Ploomber Cloud account](https://www.platform.ploomber.io/applications)
- A Dockerfile
- Your code

Note: Docker deployment option is available exclusively to Pro, Teams, and Enterprise users. Start your 10-day free trial [here.](https://ploomber.io/pricing/)

There are two ways you can deploy it on Ploomber Cloud: via (1) [Graphical User Interface](https://docs.cloud.ploomber.io/en/latest/quickstart/app.html), and (2) [Command Line Interface](https://docs.cloud.ploomber.io/en/latest/user-guide/cli.html). Let's take a look at the CLI method.

### Command Line Interface

If you haven't installed `ploomber-cloud`, run
```sh
pip install ploomber-cloud
```

Then, set your API key following to [this documentation](https://docs.cloud.ploomber.io/en/latest/quickstart/apikey.html).
```sh
ploomber-cloud key YOURKEY
```

Navigate to your project directory where your Dockerfile is located and initialize the project. Confirm the inferred project type (Docker) when prompted.
```sh
cd <project-name>
ploomber-cloud init
```

Now, deploy your application.
```sh
ploomber-cloud deploy
```

Once its deployment is complete, access your endpoints deployed on Ploomber Cloud using your app's URL. For example, you can send a `GET` request with
```sh
curl -X 'GET' 'https://<id>.ploomberapp.io/health_check'
```