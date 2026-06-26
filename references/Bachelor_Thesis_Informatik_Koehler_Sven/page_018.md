### 2.3 Prototyping

For this work lots of standalone prototypes and a small testing framework are created. Most of the machine learning steps are grouped by their responsibility and encapsulated into small classes to loose the dependencies. All prototypes are written with Python 3.5.0. The next sections gives a short overview about the used libraries. For this prototypes classes were build around every classifier, vectorizer and preprocessing step to abstract the used library and to create flexible and replaceable modules. Most of the computational work is done on the local machine. Heavy calculations, extensive grid searchs and all tests with the Convolutional Network (CNN) has been done on a GPU cluster. This cluster has 8 x Tesla P100, with 16GB RAM on each.

#### 2.3.1 Python Developing

Python is an interpreted, object-oriented programming language similar to PERL. It is designed by Guido van Rossum. Python is an open source software and supports multiple programming paradigms, including object-oriented, imperative, functional programming and procedural styles. Python comes with a huge and comprehensive standard library. For this project Python 3.5.2 was used. All dependencies, libraries and further frameworks are defined in a requirements file and portable due to virtual environment. The source code itself is stored in a SAP owned Github-repository.

#### 2.3.2 Text processing with NLTK

According to nltk.org NLTK is a leading platform for building Python programs to work with human language data. It provides easy-to-use interfaces to over 50 corporal and lexical resources such as WordNet, along with a suite of text processing libraries for classification, tokenization, stemming, tagging, parsing, and semantic reasoning, wrappers for industrial-strength NLP libraries and an active discussion forum. For this thesis NLTK 3.2.3 was used. [Loper und Bird]
