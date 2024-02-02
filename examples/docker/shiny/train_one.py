from datetime import datetime

import tensorflow as tf
from sklearn.model_selection import train_test_split

from pymongo.errors import OperationFailure
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

URI = "mongodb+srv://neelashasen:ZOT47WMuXCAKZZqK@cluster0.nshn6td.mongodb.net/?retryWrites=true&w=majority"

# Create a new client and connect to the server
client = MongoClient(URI, server_api=ServerApi('1'))

# Send a ping to confirm a successful connection
try:
    client.admin.command('ping')
    print("Successfully connected to MongoDB!")
except Exception as e:
    raise ConnectionError(str(e)) from e

db = client.myDatabase
my_collection = db["accuracy_scores"]


class TrackLossandAccuracyCallback(tf.keras.callbacks.Callback):

    def __init__(self, model_name):
        self.model_name = model_name

    def on_epoch_end(self, epoch, logs=None):
        my_collection.insert_one({'model': self.model_name, 'score': logs["accuracy"], 'timestamp': datetime.now()})


def train_model(train_images, train_labels, val_images, val_labels):
    model = tf.keras.Sequential(
        [
            tf.keras.layers.Flatten(input_shape=(28, 28)),
            tf.keras.layers.Dense(128, activation="relu"),
            tf.keras.layers.Dense(10),
        ]
    )

    model.compile(
        optimizer="adam",
        loss=tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True),
        metrics=["accuracy"],
    )

    model.fit(
        train_images,
        train_labels,
        validation_data=(val_images, val_labels),
        epochs=50,
        verbose=0,
        callbacks=[TrackLossandAccuracyCallback('model_1')],
    )


def begin():
    try:
        my_collection.drop()
    except OperationFailure as e:
        raise ConnectionError(str(e)) from e

    fashion_mnist = tf.keras.datasets.fashion_mnist
    (train_images, train_labels), (test_images, test_labels) = fashion_mnist.load_data()

    # create a validation set
    train_images, val_images, train_labels, val_labels = train_test_split(
        train_images, train_labels, test_size=0.2
    )

    # Scale the images to range (0,1)
    train_images = train_images / 255.0
    val_images = val_images / 255.0
    train_model(train_images, train_labels, val_images, val_labels)


if __name__ == "__main__":
    begin()
