import sys
import csv
import random

import numpy as np
import pandas

# based on Mingze Li's lab 6, written by Mingze Li

CHOICES = ("The Persistence of Memory", "The Starry Night", "The Water Lily Pond")

class MLPModel(object):
    def __init__(self, num_features=119, num_hidden=150, num_classes=3):
        """
        Initialize the weights and biases of this two-layer MLP.
        """
        # information about the model architecture
        self.num_features = num_features
        self.num_hidden = num_hidden
        self.num_classes = num_classes

        # weights and biases for the first layer of the MLP
        self.W1 = np.zeros([num_hidden, num_features])
        self.b1 = np.zeros([num_hidden])

        # weights and biases for the second layer of the MLP
        self.W2 = np.zeros([num_classes, num_hidden])
        self.b2 = np.zeros([num_classes])

        # initialize the weights and biases
        self.initializeParams()

        # set all values of intermediate variables (to be used in the
        # forward/backward passes) to None
        self.cleanup()

    def initializeParams(self):
        """
        Initialize the weights and biases of this two-layer MLP to be random.
        This random initialization is necessary to break the symmetry in the
        gradient descent update for our hidden weights and biases. If all our
        weights were initialized to the same value, then their gradients will
        all be the same!
        """
        self.W1 = np.random.normal(0, 2/self.num_features, self.W1.shape)
        self.b1 = np.random.normal(0, 2/self.num_features, self.b1.shape)
        self.W2 = np.random.normal(0, 2/self.num_hidden, self.W2.shape)
        self.b2 = np.random.normal(0, 2/self.num_hidden, self.b2.shape)

    def forward(self, X):
        """
        Compute the forward pass to produce prediction for inputs.

        Parameters:
            `X` - A numpy array of shape (N, self.num_features)

        Returns: A numpy array of predictions of shape (N, self.num_classes)
        """
        return do_forward_pass(self, X) # To be implemented below

    def backward(self, ts):
        """
        Compute the backward pass, given the ground-truth, one-hot targets.

        You may assume that the `forward()` method has been called for the
        corresponding input `X`, so that the quantities computed in the
        `forward()` method is accessible.

        Parameters:
            `ts` - A numpy array of shape (N, self.num_classes)
        """
        return do_backward_pass(self, ts) # To be implemented below

    def loss(self, ts):
        """
        Compute the average cross-entropy loss, given the ground-truth, one-hot targets.

        You may assume that the `forward()` method has been called for the
        corresponding input `X`, so that the quantities computed in the
        `forward()` method is accessible.

        Parameters:
            `ts` - A numpy array of shape (N, self.num_classes)
        """
        return np.sum(-ts * np.log(self.y)) / ts.shape[0]
    
    def accuracy(self, ts):
        """
        Compute accuracy
        """
        rights = 0
        wrongs = 0
        for i in range(ts.shape[0]):
            if (ts[i][np.argmax(self.y[i])] == 1):
                rights+= 1
            else:
                wrongs+= 1
        return float(rights) / (rights + wrongs)

    def update(self, alpha):
        """
        Compute the gradient descent update for the parameters of this model.

        Parameters:
            `alpha` - A number representing the learning rate
        """
        self.W1 = self.W1 - alpha * self.W1_bar
        self.b1 = self.b1 - alpha * self.b1_bar
        self.W2 = self.W2 - alpha * self.W2_bar
        self.b2 = self.b2 - alpha * self.b2_bar

    def cleanup(self):
        """
        Erase the values of the variables that we use in our computation.
        """
        # To be filled in during the forward pass
        self.N = None # Number of data points in the batch
        self.X = None # The input matrix
        self.m = None # Pre-activation value of the hidden state, should have shape
        self.h = None # Post-RELU value of the hidden state
        self.z = None # The logit scores (pre-activation output values)
        self.y = None # Class probabilities (post-activation)
        # To be filled in during the backward pass
        self.z_bar = None # The error signal for self.z2
        self.W2_bar = None # The error signal for self.W2
        self.b2_bar = None # The error signal for self.b2
        self.h_bar = None  # The error signal for self.h
        self.m_bar = None # The error signal for self.z1
        self.W1_bar = None # The error signal for self.W1
        self.b1_bar = None # The error signal for self.b1

def softmax(z):
    """
    Compute the softmax of vector z, or row-wise for a matrix z.
    For numerical stability, subtract the maximum logit value from each
    row prior to exponentiation (see above).

    Parameters:
        `z` - a numpy array of shape (K,) or (N, K)

    Returns: a numpy array with the same shape as `z`, with the softmax
        activation applied to each row of `z`
    """
    if (len(z.shape) > 1):
      new_z = np.zeros(z.shape)
      for row in range(0, new_z.shape[0]):
        new_z[row] = softmax(z[row])
      return new_z
    else:
      max_z = np.max(z)
      exps = np.exp(z - max_z)
      total = np.sum(exps)
      return (exps / total)

def make_onehot(indicies, total=4):
    """
    Convert indicies into one-hot vectors by
    first creating an identity matrix of shape [total, total],
    then indexing the appropriate columns of that identity matrix.

    Parameters:
        `indices` - a numpy array of some shape where
                    the value in these arrays should correspond to category
                    indices (e.g. note values between 0-127)
        `total` - the total number of categories (e.g. total number of notes)

    Returns: a numpy array of one-hot vectors
        If the `indices` array is shaped (N,)
           then the returned array will be shaped (N, total)
        If the `indices` array is shaped (N, D)
           then the returned array will be shaped (N, D, total)
        ... and so on.
    """
    I = np.eye(total)
    return I[indicies]

# def get_X_t(D):
#     """
#     Generate the data matrix "X" and target vector "t" from a data set "D",

#     Parameters:
#         `D` - a list of pairs of the form (x, t), returned from
#               the function `gen_input_output`

#     Returns: a tuple (X, t) where
#         `X` - a numpy array of shape (N, D), the data matrix
#         `t` - a numpy array of shape (N,),
#               with each value representing the index of the target note
#     """
#     t = np.array([next_note for seq, next_note in D])
#     X_ids = np.array([seq for seq, next_note in D])
#     X = make_onehot(X_ids)
#     X = X.reshape(X.shape[0], -1)
#     return X,t

def do_forward_pass(model, X):
    """
    Compute the forward pass to produce prediction for inputs.

    This function also keeps some of the intermediate values in
    the neural network computation, to make computing gradients easier.

    For the ReLU activation, you may find the function `np.maximum` helpful

    Parameters:
        `model` - An instance of the class MLPModel
        `X` - A numpy array of shape (N, model.num_features)

    Returns: A numpy array of predictions of shape (N, model.num_classes)
    """
    model.N = X.shape[0]
    model.X = X
    model.m = (X @ model.W1.T) + model.b1 # DONE - the hidden state value (pre-activation)
    model.h = np.maximum(model.m, 0) # DONE - the hidden state value (post ReLU activation)
    model.z = (model.h @ model.W2.T) + model.b2 # DONE - the logit scores (pre-activation)
    model.y = softmax(model.z) # DONE - the class probabilities (post-activation)
    return model.y


def do_backward_pass(model, ts):
    """
    Compute the backward pass, given the ground-truth, one-hot targets.

    You may assume that `model.forward()` has been called for the
    corresponding input `X`, so that the quantities computed in the
    `forward()` method is accessible.

    The member variables you store here will be used in the `update()`
    method. Check that the shapes match what you wrote in Part 2.

    Parameters:
        `model` - An instance of the class MLPModel
        `ts` - A numpy array of shape (N, model.num_classes)
    """
    # print("backpass begins")
    model.z_bar = (model.y - ts) / model.N
    # print(model.z_bar)
    model.W2_bar = model.z_bar.T @ model.h # TODO
    # print(model.W2_bar.shape)
    # print(model.W2_bar)
    # model.b2_bar = np.ones(model.z_bar.shape[0]).T @ model.z_bar # TODO
    model.b2_bar = np.sum(model.z_bar, axis=0)
    # print(model.b2_bar)
    model.h_bar = model.z_bar @ model.W2 # TODO
    # print(model.h_bar.shape)
    # print(model.h_bar)
    model.m_bar = model.h_bar * np.where(model.m > 0, 1, 0) # TODO
    # print(model.m_bar)
    model.W1_bar = model.m_bar.T @ model.X # TODO
    # print(model.W1_bar.shape)
    # print(model.W1_bar)
    # model.b1_bar = np.ones(model.z_bar.shape[0]).T @ model.m_bar # TODO
    model.b1_bar = np.sum(model.m_bar, axis=0)
    # print(model.b1_bar)

def train_sgd(model, X_train, t_train,
              alpha=0.1, n_epochs=0, batch_size=100,
              X_valid=None, t_valid=None,
              w_init=None, plot=True):
    '''
    Given `model` - an instance of MLPModel
          `X_train` - the data matrix to use for training
          `t_train` - the target vector to use for training
          `alpha` - the learning rate.
                    From our experiments, it appears that a larger learning rate
                    is appropriate for this task.
          `n_epochs` - the number of **epochs** of gradient descent to run
          `batch_size` - the size of each mini batch
          `X_valid` - the data matrix to use for validation (optional)
          `t_valid` - the target vector to use for validation (optional)
          `w_init` - the initial `w` vector (if `None`, use a vector of all zeros)
          `plot` - whether to track statistics and plot the training curve

    Solves for model weights via stochastic gradient descent,
    using the provided batch_size.

    Return weights after `niter` iterations.
    '''
    # as before, initialize all the weights to zeros
    w = np.zeros(X_train.shape[1])

    train_loss = [] # for the current minibatch, tracked once per iteration
    valid_loss = [] # for the entire validation data set, tracked once per epoch
    train_accuracy = []
    valid_accuracy = []

    # track the number of iterations
    niter = 0

    # we will use these indices to help shuffle X_train
    N = X_train.shape[0] # number of training data points
    indices = list(range(N))

    for e in range(n_epochs):
        random.shuffle(indices) # for creating new minibatches

        for i in range(0, N, batch_size):
            if (i + batch_size) > N:
                # At the very end of an epoch, if there are not enough
                # data points to form an entire batch, then skip this batch
                continue

            indices_in_batch = indices[i: i+batch_size]
            X_minibatch = X_train[indices_in_batch, :]
            t_minibatch = t_train[indices_in_batch]

            # gradient descent iteration
            model.cleanup()
            model.forward(X_minibatch)
            model.backward(t_minibatch)
            model.update(alpha)

            if plot:
                # Record the current training loss values
                train_loss.append(model.loss(t_minibatch))
                train_accuracy.append(model.accuracy(t_minibatch))
            niter += 1

        # compute validation data metrics, if provided, once per epoch
        if plot and (X_valid is not None) and (t_valid is not None):
            model.cleanup()
            model.forward(X_valid)
            valid_loss.append((niter, model.loss(t_valid)))
            valid_accuracy.append((niter, model.accuracy(t_valid)))

    if plot:
        # plt.title("SGD Training Curve Showing Loss at each Iteration")
        # plt.plot(train_loss, label="Training Loss")
        # if (X_valid is not None) and (t_valid is not None): # compute validation data metrics, if provided
        #     plt.plot([iter for (iter, loss) in valid_loss],
        #              [loss for (iter, loss) in valid_loss],
        #              label="Validation Loss")
        # plt.xlabel("Iterations")
        # plt.ylabel("Loss")
        # plt.legend()
        # plt.show()
        print("Final Training Loss:", train_loss[-1])
        print("Final Training Accuracy:", train_accuracy[-1])
        if (X_valid is not None) and (t_valid is not None):
            print("Final Validation Loss:", valid_loss[-1])
            print("Final Validation Accuracy:", valid_accuracy[-1])
    
    