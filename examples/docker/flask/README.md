#  App

This Flask app serves a machine learning model trained on the `Walmart Recruiting - Store Sales Forecasting` dataset for predicting store sales.

## Getting Started

To get started with this Flask app, follow these steps:

1. Run the `walmart_sales.ipynb` notebook to generate the trained model `walmart_sales_rf.joblib`.

2. Create a zip file from `Dockerfile`, `app.py`, `walmart_sales_rf.joblib`, `static/` and `templates/`.

3. Login to your [Ploomber Cloud](https://ploomber.io/) account.

2. Follow the [steps](https://docs.cloud.ploomber.io/en/latest/apps/flask.html) for deploying a Flask application and upload the `app.zip`.

## How to use

Enter valid inputs for predicting the sales. Mandatory inputs are `Store`, `Dept`, `Year`, `Month` and `Week`. `Size` should be an integer and `Markdown` values are of float type.

**Sample Input**:

'Store':9\
'Dept':72\
'IsHoliday':True\
'Type':'B'\
'Year':2012\
'Month':11\
'Week':47

The **Show Charts** button can be clicked to display the `feature correlation` and `feature importance` charts.