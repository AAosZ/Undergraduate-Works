import pickle
from sklearn.metrics import confusion_matrix, classification_report
import seaborn as sns
import matplotlib.pyplot as plt

import pandas
import numpy as np
from numpy.typing import NDArray

import model

# written by Mingze Li

# read X and T
with open('x_and_t.pkl', 'rb') as f:
    x_and_t: tuple[NDArray, NDArray] = pickle.load(f)
X, T = x_and_t

features = X.shape[1]
hidden = 1500
classes = 3

print("features: " + str(features) + " hidden perceptrons: " + str(hidden) + " classes: " + str(classes))

# set up training and valid sets
indices = np.random.permutation(len(X))

# train_end = int(0.7 * len(X))
# val_end = int(0.85 * len(X))
train_end = int(0.8 * len(X))

train_id = indices[:train_end]
# valid_id = indices[train_end:val_end]
# test_id = indices[val_end:]
valid_id = indices[train_end:]

# X_train, X_valid, X_test = X[train_id], X[valid_id], X[test_id]
# t_train, t_valid, t_test = T[train_id], T[valid_id], T[test_id]
X_train, X_valid = X[train_id], X[valid_id]
t_train, t_valid = T[train_id], T[valid_id]
print("training size: " + str(X_train.shape[0]))
print("valid size: " + str(X_valid.shape[0]))

trained_model = model.MLPModel(features, hidden, classes)

# train the model
model.train_sgd(trained_model, alpha=0.03, X_train=X_train, t_train=t_train,
                X_valid=X_valid, t_valid=t_valid, batch_size=100, n_epochs=400)

# --- Get predictions using the forward method ---
# Clean up and run forward pass on validation data
trained_model.cleanup()
val_predictions = trained_model.forward(X_valid)

# Convert predictions to class labels (get index of highest probability)
val_pred_classes = np.argmax(val_predictions, axis=1)

# Convert true labels if they're one-hot encoded
# Check if t_valid is already integer labels or one-hot
if len(t_valid.shape) > 1 and t_valid.shape[1] > 1:
    # t_valid is one-hot encoded
    val_true_classes = np.argmax(t_valid, axis=1)
else:
    # t_valid is already integer labels
    val_true_classes = t_valid

# Compute confusion matrix
cm = confusion_matrix(val_true_classes, val_pred_classes)

# Plot confusion matrix
plt.figure(figsize=(10, 8))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues')
plt.xlabel('Predicted')
plt.ylabel('Actual')
plt.title('Confusion Matrix')
plt.show()

# Get per-class metrics
print("\nClassification Report:")
print(classification_report(val_true_classes, val_pred_classes))

# Print per-class accuracy from confusion matrix
per_class_acc = cm.diagonal() / cm.sum(axis=1)
print("\nPer-class accuracy:")
for i in range(classes):
    print(f'  Class {i} accuracy: {per_class_acc[i]:.3f}')

# store model
with open('model.pkl', 'wb') as f:
    pickle.dump(trained_model, f)

# store the training, valid, and test sets
with open('train_valid_test.pkl', 'wb') as f:
    pickle.dump((X_train, t_train), f)
    pickle.dump((X_valid, t_valid), f)
    # pickle.dump((X_test, t_test), f)
