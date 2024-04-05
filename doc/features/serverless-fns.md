# Serveless functions

```{important}
`@functions.serverless` supports Python 3.9, 3.10, and 3.11
```

```{important}
The serverless functions is free while in beta. Community users get 10 calls per day,
PRO users get 100 calls per day.
```

In many applications, keeping hardware running 24/7 is wasteful (and expensive!) since
it's likely that some of your CPUs and memory are idle most of the time. In such cases,
you can save money by using serverless functions: you deploy an application with
small resources (say 0.5 CPU and 1GB of RAM) and delegate compute-intensive
operations to a serverless function.

## Use case: ML model predictions

Assume you're developing a Flask application to make predictions from a ML model
(assume the model requires 2CPUs and 6GB of RAM), your code might look like this:

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

For this app to work, you'd need to deploy an app with 2 CPUs and 6 GB, which costs
$85.4 monthly! Moving the heavy workload into a serverless function can reduce your
bill significantly. Let's revisit the example:


```python
from flask import Flask, request, jsonify
from ploomber_cloud import functions


app = Flask(__name__)


@functions.serverless(requirements=["scikit-learn==1.4.0"])
def predict(input_data):
    from my_project import load_model
    model = load_model()
    return model.predict(input_data)

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()
    input_data = data['input_data']
    # predict runs in an ephemeral container and shuts down after it's done
    prediction = predict(input_data)
    return jsonify({'prediction': prediction})
```

The code changes are minimal, but this new architecture can save you a lot of money.
Since Flask doesn't consume lots of resources, you can deploy this app with 0.5 CPU
and 1GB, then, whenever the `/predict` endpoint gets a request, the `predict` function
will run in an ephemeral container. Assuming the model takes a few seconds to perform a
prediction, you can do thousands of predictions for $1!

Since the resources are ephemeral, this will impact prediction time, as there is some
start overhead, but in most cases, this is an acceptable tradeoff.

## User guide

This section will cover the basics of using serverless functions. Before continuing,
install the client package:

```sh
pip install ploomber-cloud --upgrade
```

```{important}
Ensure you're running the latest version of `ploomber-cloud` since the API will change
over the beta period.
```

### Decorating functions

To convert your function into a serverless function, add the `@functions.serverless`
decorator, and pass any `requirements`, they'll be installed when your function is
executed:

```python
from ploomber_cloud import functions

@functions.serverless(requirements=["numpy==1.26.4"])
def random_array(size):
    import numpy as np
    return np.random.rand(size)
```


```{important}
The first execution is likely to take more time since dependencies must be installed,
subsequent executions will use the cache.
```

### Data types

If your function returns a data type that requires a third-party package (for example,
a numpy array), then, the environment that receives the resuslts must also have the
same package and version of such package:

```python
from ploomber_cloud import functions

@functions.serverless(requirements=["numpy==1.26.4"])
def random_array(size):
    import numpy as np
    return np.random.rand(size)

# this will fail if numpy is not installed locally
arr = random_array(100)
```

To fix it, install `numpy` locally or return an object that doesn't require it:

```python
from ploomber_cloud import functions

@functions.serverless(requirements=["numpy==1.26.4"])
def random_array(size):
    import numpy as np
    # no need to install numpy anymore!
    return [float(x) for x in np.random.rand(size)]

arr = random_array(100)
```

### Imports

All packages that your serverless function uses must be imported inside the function:


```python
from ploomber_cloud import functions
import numpy as np

@functions.serverless(requirements=["numpy==1.26.4"])
def random_array(size):
    # need to add all imports here!
    import numpy as np
    return np.random.rand(size)

arr = random_array(100) + np.random.rand(100)
```

(task-queues)=
## Task queues

If your application performs long-running tasks, it's a good idea to run them in the
background. You can run background tasks by calling `.background()` in decorated
functions:

```python
from ploomber_cloud import functions

@functions.serverless(requirements=["numpy==1.26.4"])
def random_array(size):
    # need to add all imports here!
    import numpy as np
    return np.random.rand(size)


# run function in the background, returns immediately with a job_id
job_id = random_array.background(10)

# returns a dictionary with 'status' and 'traceback'
status = functions.get_job_status(job_id)

# if status['status'] == 'SUCCEEDED', you can retrieve the output
result = functions.get_result_from_remote_function(job_id)

# if status['status'] == 'SUBMITTED', the function is running
# if status['status'] == 'FAILED', you can see the error message
print(status["traceback"])
```

## Resources

Serverless functions are currently limited to a maximum of 6GB and 10 minutes of
runtime. The output of each function is also limited to 100MB. If you need to increase
this quota, contact us at [contact@ploomber.io](mailto:contact@ploomber.io).

