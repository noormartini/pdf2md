uments which are often ironically or slang based texts often looses their sentiment direction by automatic translation.

The second idea was to create an own Twitter-based dataset. For this idea a Twitter crawler was build. Actually Twitter offers a search where language and the possible sentiment can be chosen. This search is accessible by the developer search-API. Unfortunately the sentiment property is not available for automatic requests. Unfortunately the legal situation is not clear and the clarification will probably take a long time.

Most of the German SA papers are based on datasets from the Interest Group on German Sentiment Analysis (IGGSA). The datasets provided are mostly dictionary based. Due to the point that this research should not only build on dictionary based approaches, the decision was made to work with English datasets. Otherwise the focus of this work would have been changed towards the field of pure data science and data generation.

Most of the English papers about SA worked with labelled Twitter feeds, Amazon product reviews or Movie Reviews. Twitter feeds are often barely objective and even humans are not able to tell the sentiment. The Amazon product review dataset seemed to be to computationally expensive. It consists of around 35 million reviews from Amazon from the last 18 years. This led to the decision to use movie reviews. To reduce the complexity only binary labelled movie reviews were used. To achieve a better generalization three different movie review sources were mixed. Every data source has a different average review length. The mixed dataset is balanced with the number of positive and negative reviews. The following sections explains them in more detail. For the visualization part a English word list from the University of Illinois was added.

#### 2.2.1 Aclimdb Movie Reviews

This dataset from the Stanford University Maas u. a. [2011] contains 50,000 reviews split evenly into 25k train and 25k test sets. The overall distribution of labels is balanced (25k pos and 25k neg). The dataset also includes additional 50,000 unlabelled documents for unsupervised learning.

In the entire collection, no more than 30 reviews are allowed for any given movie because reviews for the same movie tend to have correlated ratings. Further, the train and test sets contain a disjoint set of movies, so no significant performance is
