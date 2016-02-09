import difflib
import nltk
from nltk.corpus import wordnet
import re
import cdec, cdec.score
import math
from RIBES import *
from sbleu import init_sbleu, sbleu
from config import *

stopwords=STOP_WORDS

init_sbleu('synonyms.db')

def allShapesOf(line):
    words=re.findall(r'\w+', line.lower())
    words=list(filter(lambda x: x not in stopwords, words))
    wordsCopy=words[:]
    shapes=[]
    for i, word in enumerate(wordsCopy):
        words.pop(i)
        for synonym in synonyms(word):
            words.insert(i, synonym)
            shapes.append(' '.join(words))
            words.pop(i)
        words.insert(i, word)
    return shapes
def cmp_synonyms(line1, line2, cmpfn):
    # compare two lines by best result of intersection of words divided by union of words, when all line1 words synonyms are tested
    words2=re.findall(r'\w+', line2.lower())
    words2=list(filter(lambda x: x not in stopwords, words2))
    words2Line=' '.join(words2)    
    maxRate=0
    for shape in allShapesOf(line1):
        rate=cmpfn(shape, words2Line)
        maxRate=max(rate, maxRate)
    return maxRate


def cmp_sequence_synonyms(line1, line2):
    return cmp_synonyms(line1, line2, cmp_sequence)
def cmp_sequence_synonyms_quick(line1, line2):
    return cmp_synonyms(line1, line2, cmp_sequence_quick)
def cmp_sequence_synonyms_2D(line1, line2):
    maxRate=0
    for shape1 in allShapesOf(line1):
        for shape2 in allShapesOf(line2):
            rate=cmp_sequence_real_quick(shape1, shape2)
            maxRate=max(rate, maxRate)
    return maxRate


def cmp_set(line1, line2):
    # compare two lines by intersection of words divided by union of words
    words1=re.findall(r'\w+', line1.lower())
    words2=re.findall(r'\w+', line2.lower())
    words1=set(filter(lambda x: x not in stopwords, words1))
    words2=set(filter(lambda x: x not in stopwords, words2))
    if len(words1)+len(words2)==0: return 0
    return len(words1.intersection(words2))*1.0/(len(words1)+len(words2))

def cmp_sequence_stopwords(line1, line2):
    # remove stop words and compare two lines with difflib.SequenceMatcher
    words1=re.findall(r'\w+', line1.lower())
    words2=re.findall(r'\w+', line2.lower())
    words1=set(filter(lambda x: x not in stopwords, words1))
    words2=set(filter(lambda x: x not in stopwords, words2))
    line1=' '.join(words1)
    line2=' '.join(words2)
    return difflib.SequenceMatcher(None, line1, line2).ratio()    

def cmp_sequence(line1, line2):
    # compare two lines with difflib.SequenceMatcher
    return difflib.SequenceMatcher(None, line1, line2).ratio()
def cmp_sequence_quick(line1, line2):
    # compare two lines with difflib.SequenceMatcher
    return difflib.SequenceMatcher(None, line1, line2).quick_ratio()
def cmp_sequence_real_quick(line1, line2):
    # compare two lines with difflib.SequenceMatcher
    return difflib.SequenceMatcher(None, line1, line2).real_quick_ratio()

def cmp_RIBES(line1, line2):
    return RIBESevaluator().eval([line1], [[line2]])[0]

def cmp_cdec(f, line1, line2):
    score=getattr(cdec.score, f)(line1).evaluate(line2).score
    if f in ('CER', 'TER'): score=1-score
    if math.isnan(score): score=0
    return score

def cmp_BLEU(line1, line2):
    return cmp_cdec('BLEU', line1, line2)
def cmp_CER(line1, line2):
    return cmp_cdec('CER', line1, line2)
def cmp_SSK(line1, line2):
    return cmp_cdec('SSK', line1, line2)
def cmp_TER(line1, line2):
    return cmp_cdec('TER', line1, line2)

def cmp_SBLEU(line1, line2):
    c = sbleu(line1, line2)
    return c[SBLEU_NGRAM][2]

def synonyms(word):
    syns = wordnet.synsets(word)
    synsWords=[l.name for s in syns for l in s.lemmas]
    return list(set(synsWords)) if synsWords!=[] else [word]

if __name__=='__main__':
    l=[cmp_BLEU, cmp_SBLEU, cmp_CER, cmp_SSK, cmp_TER, cmp_RIBES, cmp_sequence, cmp_sequence_stopwords, cmp_set, cmp_sequence_synonyms_quick, cmp_sequence_synonyms, cmp_sequence_synonyms_2D]
    s1='It is just a small test'
    s2='It is not just a small test'
    for f in l:
        print(f.__name__, f(s1, s2))
