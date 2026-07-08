This approach performs morphological analysis at character level. They show that networks do not require the knowledge of words or semantic and syntactic structure of a language [Zhang u. a., 2015] [Cao und Rei, 2016].

## 3.4 Hyper-parameter tuning for machine learning

Hyper-parameter tuning means in the field of machine learning means to find the best working machine learning pipeline by optimizing all indirectly learned parameters within the estimator.

One way of optimizing the parameters can be to investigate the role of preprocessing, stopword removal, tokenization, stemming, POS-tagging [Haddi u. a., 2013] [Kotsiantis u. a., 2006] [Copestack, 2004] [Das und Balabantaray, 2014] [Manning u. a., 2009a] [Ghag, 2014].

Another approach is to find the best working overall architecture of the neural network or machine learning pipeline for a specific task. This leads to the question whether one should use Doc2Vec, Word2Vec or Char2Vec as vector space model [Řehůřek und Sojka, 2010], a CBOW or Skipgram-based architecture for the embedding part [Mikolov u. a., 2013a] [Mikolov u. a., 2013b]. Optimization by better generalisation through dropout-layers [Srivastava u. a., 2014] or better accuracies through deeper layers and new network architectures or classification approaches [Szegedy u. a., 2016a] [Szegedy u. a., 2016b], [LeCun u. a., 1998] [Cortes und Vapnik, 1995].

Last but not least each parameter itself can be optimized. This could concern the vectorizing, feature weighting, feature selection, normalization and classification modules. Instead of doing these parameter tuning in a brute force way, there are approaches like the Bayesian Optimization. In this work, J. Snoek considered the automatic tuning problem within the framework of Bayesian optimization, in which a learning algorithm's generalization performance is modelled as a sample from a Gaussian process [Snoek u. a., 2012]. Others have developed random search or gradient based optimization techniques [Pedregosa u. a., 2011] [Bergstra JAMESBERG-STRA und Yoshua Bengio YOSHUABENGIO, 2012] [Abadi u. a., 2015a] [Chapelle u. a., 2002].
