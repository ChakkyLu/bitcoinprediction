# import nltk
# nltk.download()
#
from nltk.corpus import wordnet

dog = wordnet.synset('market.')
print(dog.lemma_names())
