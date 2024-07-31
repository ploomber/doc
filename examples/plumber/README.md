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
curl -X 'POST' 'http://127.0.0.1/predict_petal_length' -d '{"petal_width": 1.2, "sepal_length": 3.5, "sepal_width": 2.1, "species": "setosa"}' -H "Content-Type: application/json"
```

### Plot Actual vs Predicted (GET)
To download a plot comparing actual and predicted petal lengths:
```sh
curl -X 'GET' 'http://127.0.0.1/plot_actual_vs_predicted' --output test.png
```