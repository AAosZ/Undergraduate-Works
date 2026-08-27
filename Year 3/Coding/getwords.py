import pandas as pd

# Load the CSV

dataset = pd.read_csv("ml_challenge_dataset.csv")



counts1 = dataset["Describe how this painting makes you feel."].str.lower().str.split(r'\W+', expand=True).stack().value_counts()
# counts2 = dataset["What season does this art piece remind you of?"].str.lower().str.split(r'\W+', expand=True).stack().value_counts()
counts3 = dataset["If this painting was a food, what would be?"].str.lower().str.split(r'\W+', expand=True).stack().value_counts()
counts4 = dataset["Imagine a soundtrack for this painting. Describe that soundtrack without naming any objects in the painting."].str.lower().str.split(r'\W+', expand=True).stack().value_counts()

top = 100

print("Counts Describe how this painting makes you feel:")
print(counts1.head(top).to_string())
# print("Counts 2:")
# print(counts2.head(top))
print("Counts If this painting was a food, what would be:")
print(counts3.head(top).to_string())
print("Counts Imagine a soundtrack for this painting. Describe that soundtrack without naming any objects in the painting:")
print(counts4.head(top).to_string())