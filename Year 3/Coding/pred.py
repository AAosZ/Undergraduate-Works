# basic python imports are permitted
import csv
import pickle

# numpy and pandas are also permitted
import numpy as np
import pandas as pd

import model
import convert_data

filename = "model.pkl"
CHOICES = ("The Persistence of Memory", "The Starry Night", "The Water Lily Pond")

# Load the model
with open(filename, "rb") as f:
    loaded_model: model.MLPModel = pickle.load(f)

df = pd.read_pickle('model.pkl')
# print(df.head())
print(f"Loaded model with {loaded_model.num_features} features, {loaded_model.num_hidden} hidden units, {loaded_model.num_classes} classes")

def predict(x):
    """
    Helper function to make prediction for a given input x.
    This code is here for demonstration purposes only.
    """
    results = loaded_model.forward(np.array(x))
    y = CHOICES[np.argmax(results)]

    # return the prediction
    return y


def predict_all(filename):
    """
    Make predictions for the data in filename
    """
    # read the file containing the test data
    # you do not need to use the "csv" package like we are using
    # (e.g. you may use numpy, pandas, etc)
    data = csv.DictReader(open(filename))

    predictions = []
    for test_example in data:
        # obtain a prediction for this test example
        pred = predict(convert_data.row_to_x(test_example))
        predictions.append(pred)

    return predictions

