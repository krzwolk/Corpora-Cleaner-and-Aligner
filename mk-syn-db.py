# This scritp creates a shelve db from synonyms of all wordnet words. 
# The final db is a dictionary like object.
# db[word] = [wordnet synonyms of this word]


import sys
import shelve
from nltk.corpus import wordnet

syn=lambda name: list(set([j for i in wordnet.synsets(name) for j in i.lemma_names]+[name]))

out_filename=sys.argv[1]
d=shelve.open(out_filename)
d.clear()
for i in wordnet.all_lemma_names():
    d[i]=syn(i)
d.close()
