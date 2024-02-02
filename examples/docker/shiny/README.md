# Model monitoring application

This app is built on Shiny and allows you to visualize model training accuracy scores in realtime in 2 steps:

* Train multiple models with different parameters locally, and store the accuracy scores to a remote database at the end of every epoch.
* The visualisation application dynamically detects changes in the remote database and generates a plot as the training progresses.

## Connecting to MongoDB Cloud

For the purpose of this tutorial we will use the `MongoDB Atlas` cloud database. It allows users to host a database for free.
Let's see the steps for creating a cluster:

First create an account on [MongoDB cloud](https://www.mongodb.com/atlas/database) and create a new project:

![](./static/create-project.png)

Then select `Create deployment` and select the free tier `M0` or your desired tier. 

In the `Security Quickstart` page, select your authentication type. For this tutorial we have generated a username and password.

Select the `Cloud Environment` and open the `Network Access Page` in a new tab.

![](./static/network-access.png)

Now select `ALLOW ACCESS FROM ANYWHERE` and confirm to allow all IP addresses to connect to the cluster.

![](./static/ip-access.png)

Once you have completed the access rules setup, select the `CONNECT` button on the `Overview` page to get the connection details. Specifically, copy the connection string and replace the `URI` variable value in `app-core.py`, `train_one.py` and `train_two.py`

![](./static/connect.png)

## Deploy application

Create a zip file using `Dockerfile`, `app-core.py` and `requirements.txt` and deploy this file to Ploomber cloud.
Refer to the [Shiny deployment documentation](https://docs.cloud.ploomber.io/en/latest/apps/shiny.html) for more details.
Once the `VIEW APPLICATION` button is enabled, you can start the training script and monitor the training.

## Train models

We will use the [MNIST dataset](https://www.tensorflow.org/datasets/catalog/mnist) and train two different models on the data. The models differ in the number of units in the `Dense` layer.
The training scripts write the accuracy values at the end of every epoch to the MongoDB database in a collection called `accuracy_scores`.

First create a virtual environment and install the required packages:

```bash
pip install tensorflow scikit-learn "pymongo[srv]"
```

Then run the training scripts parallely:

```bash
python train_one.py & python train_two.py & wait
```

Once the scripts are running you can monitor the accuracy scores as the training progresses on the Ploomber Cloud application deployed in above step:

![](./static/monitor.png)

Currently, the threshold for an accurate model (marked in green) is 0.9. You can modify it by setting `THRESHOLD_MID` in `app-core.py`.
