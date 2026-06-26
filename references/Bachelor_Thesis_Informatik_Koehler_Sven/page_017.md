obtained by memorizing movie-unique terms and their association with observed labels. In the labelled train/test sets, a negative review has a score <= 4 out of 10, and a positive review has a score >= 7 out of 10. Thus reviews with more neutral ratings are not included in the train/test sets. In the unsupervised set, reviews of any rating are included and there are an even number of reviews > 5 and <= 5.

#### 2.2.2 Polarity Movie Reviews

The polarity dataset comes from the Cornells University Pang und Lee [2004]. This data consists of unprocessed, unlabelled html files from the IMDb archive. The files used for this work represent a processed subset of these files. It consists of 1000 positive and 1000 negative processed reviews.

The decision weather a review is positive or negative is based on the following rules. With a five-star system (or compatible number systems): three-and-a-half stars and up are considered positive, two stars and below are considered negative. With a four-star system (or compatible number system): three stars and up are considered positive, one-and-a-half stars and below are considered negative. With a letter grade system: B or above is considered positive, C- or below is considered negative.

#### 2.2.3 Kaggle Movie Reviews

The third dataset used for this work is taken from a Sentiment Classification Task provided by Kaggle. The original data comes from opinmind.com (which is no longer active). It consists of 3995 positive and 3091 negative related reviews. Kaggle gives no further informations about this dataset.

#### 2.2.4 Sentiment word lists

A list of English positive and negative opinion words or sentiment words (around 6800 words). This list was compiled over many years starting from this first paper Hu u. a. [2004].
