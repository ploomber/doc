#  App

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

```python
from ploomber_engine import execute_notebook

_ = execute_notebook("walmart_sales.ipynb", output_path=None)
```

3. Create a zip file from `Dockerfile`, `app.py`, `walmart_sales_rf.joblib`, `static/` and `templates/`.

4. Login to your [Ploomber Cloud](https://ploomber.io/) account.

5. Follow the [steps](https://docs.cloud.ploomber.io/en/latest/apps/flask.html) for deploying a Flask application and upload the `app.zip`.

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