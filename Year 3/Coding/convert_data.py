# converts all data to X for the model
import sys
import csv
import random
import pickle
import re

import pandas
import numpy as np

def make_into_mapping(vocab):
    return {element: index for index, element in enumerate(vocab)}

def make_into_bow(data: str, mapping, size):
    """
    Return a bag of words representation of data based on mapping
    """
    X = np.zeros(size)
    for word in re.split(r'\W+', data):
        index = mapping.get(word, -1)
        X[index] = 1
    return X


HEADERS = ("unique_id", #0
           "Painting", #1
           "On a scale of 1–10, how intense is the emotion conveyed by the artwork?", #2
           "Describe how this painting makes you feel.", #3
           "This art piece makes me feel sombre.", #4
           "This art piece makes me feel content.", #5
           "This art piece makes me feel calm.", #6
           "This art piece makes me feel uneasy.", #7
           "How many prominent colours do you notice in this painting?", #8
           "How many objects caught your eye in the painting?", #9
           "How much (in Canadian dollars) would you be willing to pay for this painting?", #10
           "If you could purchase this painting, which room would you put that painting in?", #11
           "If you could view this art in person, who would you want to view it with?", #12
           "What season does this art piece remind you of?",#13
           "If this painting was a food, what would be?", #14
           "Imagine a soundtrack for this painting. Describe that soundtrack without naming any objects in the painting." #15
           )

CHOICES = ("The Persistence of Memory", "The Starry Night", "The Water Lily Pond")

vocab1 = ("calm", "time", "happy", "peaceful", "relaxed", "sad", "sky", "clocks", "life", "world", "night",
          "quiet", "warm", "everything", "nostalgic", "uneasy", "content", "peace", "nature", "melting",
          "beautiful", "awe", "bright", "serene", "wonder", "hopeful", "beauty", "down") # how this painting make feel
vocab2 = ("salad", "cream", "ice", "soup", "blueberry", "cake", "bread", "pizza", "cheese", "chocolate", "pie", 
          "sandwich", "spaghetti", "apple", "fresh", "pasta", "bowl", "cheesecake", "warm", "green", "chicken", 
          "fruit", "tea", "steak", "noodles", "rice", "strawberry", "hot", "matcha") # what food is the painting
vocab3 = ("slow", "piano", "calm", "soft", "melody", "quiet", "background", "violin", "feel", "peaceful",
          "upbeat", "light", "classical", "happy", "time", "wind", "sad", "gentle", "instruments", "low",
          "piece", "rhythm", "birds", "calming", "nature", "tempo", "fast", "flute", "chirping", "flowing",
          "track", "strings", "soothing", "guitar", "high", "bright", "sombre", "long", "relaxing", "warm",
          "ambient") # imagine soundtrack for this painting

category_room = ("bedroom", "bathroom", "office", "living", "dining") # room removed
category_who = ("friends", "family", "yourself", "strangers", "classmates") # by, with, Coworkers removed
category_season = ("spring", "summer", "fall", "winter")

headers_to_mapping = (
    (HEADERS[3], make_into_mapping(vocab1), len(vocab1)),
    (HEADERS[11], make_into_mapping(category_room), len(category_room)),
    (HEADERS[12], make_into_mapping(category_who), len(category_who)),
    (HEADERS[13], make_into_mapping(category_season), len(category_season)),    
    (HEADERS[14], make_into_mapping(vocab2), len(vocab2)), 
    (HEADERS[15], make_into_mapping(vocab3), len(vocab3)))

def csv_to_parameters(filename: str):
    data = csv.DictReader(open(filename))
    return convert(data)

def convert(data: csv.DictReader):
    X = []
    for row in data:
        X.append(row_to_x(data.fieldnames, row))
    return np.array(X)

def convert_with_t(data: csv.DictReader):
    X = []
    T = []
    for row in data:
        x, t = row_to_x_and_t(row)
        X.append(x)
        T.append(t)
    return np.array(X), np.array(T)
    
def row_to_x(row: dict[str, str]):
    # parameters: 
    for i in (2, 4, 5, 6, 7, 8, 9):
        if (len(row[HEADERS[i]]) < 1):
            if (i == 2):
                row[HEADERS[i]] = "5"
            else:
                row[HEADERS[i]] = "3"
    x = [float(row[HEADERS[2]]), float(row[HEADERS[4]][0]), 
         float(row[HEADERS[5]][0]), float(row[HEADERS[6]][0]), float(row[HEADERS[7]][0]), 
         float(row[HEADERS[8]]), float(row[HEADERS[9]])] # all the numeric input
    for header, mapping, size in headers_to_mapping:
        x.extend(make_into_bow(row[header].lower(), mapping, size))

    return np.array(x)

def row_to_x_and_t(row: dict[str, str]):
    t = np.zeros(3)
    label = row[HEADERS[1]]
    if (label == CHOICES[0]):
        t[0] = 1
    elif (label == CHOICES[1]):
        t[1] = 1
    elif (label == CHOICES[2]):
        t[2] = 1
    else:
        print("Something is wrong: label " + label + " does not match any of our choices")
    return row_to_x(row), t

if __name__ == "__main__":
    data = csv.DictReader(open("cleaned_MLCHALLENGE_dataset.csv"))
    X, T = convert_with_t(data)
    with open('x_and_t.pkl', 'wb') as f:
        pickle.dump((X, T), f)