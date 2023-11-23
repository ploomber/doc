import numpy as np
import pandas as pd
from flask import Flask, request, jsonify, render_template
from joblib import load

app = Flask(__name__)
model = load('walmart_sales_rf.joblib')


def predict_input(model, single_input):
    input_df = pd.DataFrame([single_input])
    numeric_cols = model['numeric_cols']
    encoded_cols = model['encoded_cols']
    categorical_cols = model['categorical_cols']
    input_df[numeric_cols] = model['imputer'].transform(input_df[numeric_cols])
    input_df[numeric_cols] = model['scaler'].transform(input_df[numeric_cols])
    input_df[encoded_cols] = model['encoder'].transform(input_df[categorical_cols].values)
    return model['model'].predict(input_df[numeric_cols + encoded_cols])[0]


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict',methods=['POST'])
def predict():

    date = pd.to_datetime(request.form['Date'])
    input_features = {
    'Store': int(request.form['Store']), 
    'Dept': int(request.form['Dept']), 
    'IsHoliday': request.form['isHoliday'], 
    'Type': None,
    'Size': None,
    'MarkDown1': None,
    'MarkDown2': None,
    'MarkDown3': None,
    'MarkDown4': None,
    'MarkDown5': None,
    'Year': date.year,
    'Month': date.month,
    'Week': date.isocalendar().week,
    }
    predicted_price = predict_input(model, input_features)

    return render_template('index.html', prediction_text='The predicted weekly sales is $ {}'.format(round(predicted_price,2)))


if __name__ == "__main__":
    app.run(debug=False)