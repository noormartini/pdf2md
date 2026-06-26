# Chapter 3

## Related work

This section splits the related work into related areas. The following part gives an overview of the current scientific state within this areas.

### 3.1 Text classification

Automatic document classification means assigning a document to one ore more classes. This field consists of two sub-areas: Content based and request based. This thesis is related to the field of supervised, content based document classification.

A very popular method for this task is the probabilistic based Naive Bayes approach. For this method there is no explicit feature extraction necessary. A. McCallum and K. Nigam compared different models for this approach to find out whether Bernoulli or Bayesian based models works better for document classification. [McCallum und Nigam, 1998]

Most text classification systems works with supervised classification models combined with numerous variants of data preprocessing and feature vectorizing steps before to extracting the most important features of a text. [Baccianella u. a., 2010], [Hu u. a., 2004], [Manning u. a., 2009a]

The deep learning approaches integrated the feature extraction step into their first layers to create an embedding matrix as input to their hidden layers, combined with pooling, dropout and normalization layers. The fully connected last layer assigns the extracted document features to some output classes with an activation function. [Kim, 2014], [Hong]
