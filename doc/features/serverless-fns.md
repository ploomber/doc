# Serveless functions

```{important}
The serverless functions API is experimental and only available for certain customers,
if you want to get on the waitlist, send us an email
[contact@ploomber.io](mailto:contact@ploomber.io)
```

In many applications, keeping hardware running 24/7 is wasteful (and expensive!) since
it's likely that some of your CPUs and memory are idle most of the time. In such cases,
you can save money by using serverless functions: you deploy an application with
small/medium resources (say 0.5 CPU and 1GB of RAM) and delegate compute-intensive
operations to a serverless function, which are billed per second.

## Use case: ML model predictions

Assume you're developing a Flask application to make predictions from a ML model
(assume the model requires 8CPUs and 16GB of RAM), your code might look like this:

```python
from flask import Flask, request, jsonify
from my_project import load_model

app = Flask(__name__)
model = load_model()

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    input_data = data['input_data']
    return jsonify({'prediction': model.predict(input_data)})
```

For this app to work, you'd need to deploy an app with 8 CPUs and 16 GB, which costs
$313.34 monthly! Moving the heavy workload into a serverless function can reduce your
bill significantly. Let's revisit the example:


```python
from flask import Flask, request, jsonify
from ploomber_cloud import serverless


app = Flask(__name__)

# pass resources needed and pip packages
@serverless(n_cpus=4, memory="16GB", requirements=["scikit-learn"])
def predict(input_data):
    from my_project import load_model
    model = load_model()
    return model.predict(input_data)

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    input_data = data['input_data']
    return jsonify({'prediction': predict(input_data)})
```

The code changes are minimal, but this new architecture can save you a lot of money.
Since Flask doesn't consume lots of resources, you can deploy this app with 0.5 CPU
and 1GB, then, whenever the `/predict` endpoint gets a request, the `predict` function
will run in an ephemeral container.

Assuming the model takes 1s to perform a prediction, you can do 14,000 predictions
for $1!

Since the resources are ephemeral, this will impact prediction time, as there is some
start overhead, but in most cases, this is an acceptable tradeoff.

## Secrets

If your serverless function requires secrets, you can manage them from the CLI.
They are available to your function via `os.environ`

```bash
ploomber-cloud secrets --list
ploomber-cloud secrets --add NAME=VALUE
ploomber-cloud secrets --remove NAME
```