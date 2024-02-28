# Machine Learning app

A Flask app that makes predictions using an ML model.

This Flask app serves a machine learning model trained on the `Walmart Recruiting - Store Sales Forecasting` dataset for predicting store sales.

## Getting Started

To get started with this Flask app, follow these steps:

1. Download the [dataset](https://www.kaggle.com/competitions/walmart-recruiting-store-sales-forecasting/data) required for training the model. Ensure that you have the `train.csv`, `stores.csv` and `features.csv` in the same folder as `walmart_sales.ipynb`.

2. Create a new virtual environment and install the dependencies:

```bash
pip install -r requirements.txt
```

3. Run the `walmart_sales.ipynb` notebook to generate the trained model `walmart_sales_rf.joblib`. You can use [Ploomber Engine](https://engine.ploomber.io/en/latest/user-guide/running.html) to run the notebook.

```bash
pip install ploomber-engine
```

Execute the `walmart_sales.ipynb` notebook.

```bash
ploomber-engine walmart_sales.ipynb output.ipynb
```

3. Create a zip file from `Dockerfile`, `app.py`, `walmart_sales_rf.joblib`, `static/` and `templates/`.

4. Login to your [Ploomber Cloud](https://ploomber.io/) account.

5. Follow the [steps](https://docs.cloud.ploomber.io/en/latest/apps/flask.html) for deploying a Flask application and upload the `app.zip`.

## How to use

Enter valid inputs for predicting the sales. 

* `Store`: values are numbered 1-45 for 45 stores.\
* `Dept`: department number of the particular store.\
* `IsHoliday`: whether the week is a special holiday week.\
* `Date`: the week for which sales needs to be predicted.\
* `MarkDown1-5`: promotional markdowns that are being run in the specific week


**Sample Input**:

'Store': 9\
'Dept': 72\
'IsHoliday': True\
'Date': '12/08/2011'

The **Show Charts** button can be clicked to display the `feature correlation` and `feature importance` charts.

**cURL**

curl --location 'https://dashboard-id.ploomberapp.io/predict' --form 'Store="9"' --form 'Dept="12"' --form 'isHoliday="True"' --form 'Date=" 12/09/2011"' --form 'MarkDown1="123.23"' --form 'MarkDown2=""' --form 'MarkDown3="0.08"' --form 'MarkDown4=""' --form 'MarkDown5=""'
