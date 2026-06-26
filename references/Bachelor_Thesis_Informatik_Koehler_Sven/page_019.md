#### 2.3.3 Scikit-Learn as ML-Framework

Scikit-learn is a Python module for machine learning built on top of SciPy and distributed under the 3-Clause BSD license. For this work scikit-learn 0.18.2 was used. [Pedregosa u. a., 2011]

#### 2.3.4 TensorFlow as ML Framework

TensorFlow is an open source software library for numerical computation using data flow graphs. Nodes in the graph represent mathematical operations, while the graph edges represent the multidimensional data arrays (tensors) communicated between them. The flexible architecture allows you to deploy computation to one or more CPUs or GPUs in a desktop, server, or mobile device with a single API. TensorFlow was originally developed by researchers and engineers working on the Google Brain Team within Google's Machine Intelligence research organization for the purposes of conducting machine learning and deep neural networks research, but the system is general enough to be applicable in a wide variety of other domains as well. For this work tensorflow 1.0 was used. [Abadi u. a., 2015b]

### 2.4 Evaluation

After all prototypes were build up, evolved and improved, the Accuracy of each model was evaluated. The naive Bayes approach was used as baseline for this step. To improve the accuracy a deep understanding of where does the sentiment comes from was required. Investigating in this topic, the evaluation process evolved to a search for the representation of the sentiment in our text. During the evaluation phase once recognized that it is not always just the accuracy of a model that counts. Sometimes it is more important to search for the reason why one approach works.
