# Serveless functions

```{important}
The serverless functions is in beta and only available to PRO customers. Usage is
free while in beta.
```

In many applications, keeping hardware running 24/7 is wasteful (and expensive!) since
it's likely that some of your CPUs and memory are idle most of the time. In such cases,
you can save money by using serverless functions: you deploy an application with
small resources (say 0.5 CPU and 1GB of RAM) and delegate compute-intensive
operations to a serverless function.

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
from ploomber_cloud import functions


app = Flask(__name__)


@functions.remote(requirements=["scikit-learn"])
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

Assuming the model takes a few seconds to perform a prediction, you can do thousands
of predictions for $1!

Since the resources are ephemeral, this will impact prediction time, as there is some
start overhead, but in most cases, this is an acceptable tradeoff.

## User guide

### Data types

```python
from ploomber_cloud import functions

@functions.remote(requirements=["numpy"])
def random_array(size):
    import numpy as np
    return np.random.rand(size)

# this will fail if numpy is not installed locally
arr = random_array(100)
```

To fix it, either install numpy locally or return an object that doesn't require it:

```python
from ploomber_cloud import functions

@functions.remote(requirements=["numpy"])
def random_array(size):
    import numpy as np
    # no need to install numpy anymore!
    return [float(x) for x in np.random.rand(size)]

arr = random_array(100)
```

### Imports

All imports must be inside the function, even if that causes duplicates:


```python
from ploomber_cloud import functions
import numpy as np

@functions.remote(requirements=["numpy"])
def random_array(size):
    import numpy as np
    return np.random.rand(size)

arr = random_array(100) + np.random.rand(100)
```


## Task queues

```python
from ploomber_cloud import functions

@functions.remote(requirements=["numpy"])
def return_x(x):
    return x

job_id = return_x.background(10)
functions.get_job_status(job_id)
functions.get_result_from_remote_function(job_id)
```

## Resources

Serverless functions are currently limited to a maximum of 6GB and 10 minutes of
runtime. The output of each function is also limited to 100MB. If you need to increase
this quota, contact us at [contact@ploomber.io](mailto:contact@ploomber.io).

