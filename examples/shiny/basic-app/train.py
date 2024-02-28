import os
import argparse
from datetime import datetime

import tensorflow as tf
from sklearn.model_selection import train_test_split

from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi

URI = os.environ.get("MONGODB_CONNECTION_URI", "")

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
        timestamp = datetime.now()
        epoch_data = {'model': self.model_name, 'score': logs["accuracy"], 'timestamp': timestamp}
        print(f"accuracy : {logs['accuracy']}, timestamp : {timestamp.strftime('%H:%M:%S')}")
        my_collection.insert_one(epoch_data)


def train_model(train_images, train_labels, val_images, val_labels, model_name, dense_units):
    model = tf.keras.Sequential(
        [
            tf.keras.layers.Flatten(input_shape=(28, 28)),
            tf.keras.layers.Dense(int(dense_units), activation="relu"),
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
        epochs=100,
        verbose=0,
        callbacks=[TrackLossandAccuracyCallback(model_name)],
    )
    print("Training completed!")


def begin(model_name, dense_units):

    fashion_mnist = tf.keras.datasets.fashion_mnist
    (train_images, train_labels), (test_images, test_labels) = fashion_mnist.load_data()

    # create a validation set
    train_images, val_images, train_labels, val_labels = train_test_split(
        train_images, train_labels, test_size=0.2
    )

    # Scale the images to range (0,1)
    train_images = train_images / 255.0
    val_images = val_images / 255.0
    train_model(train_images, train_labels, val_images, val_labels, model_name, dense_units)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-m", "--model", required=True, help="Model name")
    parser.add_argument("-u", "--units", required=True, help="Dense layer units")
    args = parser.parse_args()
    begin(args.model, args.units)
