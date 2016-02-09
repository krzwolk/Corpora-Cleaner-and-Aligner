# This implementaion of BLEU also consider synonyms and try to give more points to sort order of words.

# [ ] 1. considering ',' and '.' as tokens
# [*] 2. rare words score
# [*] 3. brevity penalty
# [ ] 4. test of synonyms
# [*] 5. doc


import re
import os
import sys
import shelve
import optparse
import itertools
from math import log, exp
from collections import Counter

class Options():
    penalty = False
    consider_synonyms = True
    synonym_score = 0.9
    consider_rare_words = False
    rare_words_score = 1.5
    rare_words_percent = 10
    rare_words_min = 20

syndb = None
ngram_max=4
opt = Options()


def init_sbleu(path, new_opt=None, new_ngram_max=None):
    global syndb, opt, ngram_max
    if not os.path.exists(path):
        print >> sys.stderr, 'error: "%s" file not found' % path
        sys.exit(1)
    syndb=shelve.open(path)
    if new_opt:
        opt = new_opt
    if new_ngram_max:
        ngram_max = new_ngram_max

def parse_options():
    p=optparse.OptionParser('usage: %prog [options] test-file ref-file')
    p.add_option('-p', '--penalty', dest='brevity_penalty', action='store_true', help='consider brevity penalty')
    p.add_option('-n', '--no-synonyms', dest='consider_synonyms', action='store_false', default=True, help='the result will be same as BLEU')
    p.add_option('--synonym-score', dest='synonym_score', type='float', default=0.90, help='synonyms score ratio, a float between 0 and 1')
    p.add_option('-r', '--rare-words', dest='consider_rare_words', action='store_true', default=False, help='consider extra score for rare words')
    p.add_option('--rare-words-score', dest='rare_words_score', type='float', default=1.50, help='rare words score ratio, a float greater than 1')
    p.add_option('--rare-words-percent', dest='rare_words_percent', type='int', default=10, help='percent of rare words compared to all words in ref')
    p.add_option('--rare-words-min', dest='rare_words_min', type='int', default=20, help='minimum distinct words in ref needed to calculate rare words score')
    p.add_option('--synonyms-db', dest='synonyms_db', default='synonyms.db', help='synonyms database file')
    opt, args=p.parse_args()
    if len(args)!=2:
        p.error('missing input files')
    return opt, args


def ngram(seg, n):
    '''
    param seg: str, a unicode str like "a b c d"
    param n: int
    return: [str], n-grams. for n=2 and seg="a b c d" return value is ["a b", "b c", "c d"]
    This function does not clear seg, so it consider "this test." as "this" and "test." not "this" and "test"
    '''
    a=seg.split()
    assert n>0
    if n>len(a):
        return None # assert n<=len(a), 'can not create %d-gram from "%s"'%(n, seg)
    r=[]
    for i in range(len(a)-n+1):
        t=' '.join(a[i:i+n])
        r.append(t)
    return r


def synonyms(name):
    '''
    synonyms of a name from wordnet: 'hello' -> ['howdy', 'hi', 'hello', 'how do you do', 'hullo']
    name itself always is in the result.
    param name: str
    return: [str]
    '''
    l=syndb.get(name, [])
    if name not in l:
        l.append(name)
    l=[i.replace('-', ' ').replace('_', ' ') for i in l]
    return l


def find_best(word, ref):
    '''
    try to find the best choice between the word itself and all of its synonyms,
    the best is the most repeated one in the ref. if word and one of its synonyms have
    same repeat, the word is the better choice.
    param word: str, a word in test (test is not passed to this function)
    param ref: str, the ref segments
    return: srt
    '''
    if word in ('as', 'one', 'us'):
        return word
    syns=synonyms(word)
    synsc=Counter(dict([(i, ref.count(i)) for i in syns]))
    w_max, c_max=synsc.most_common()[0]
    if c_max==synsc[word]:
        return word
    return w_max


def closest_syntest_to_ref(test, ref):
    '''
    replace words of test with their synonyms to find closest sentence to the ref.
    param test: str
    param ref: str
    return: str
    '''
    return ' '.join([find_best(i, ref) for i in test.split()])


def sbleu(test, ref, rare_words=None):
    '''
    param test: str, test segments. segment is a unicode str contains words.
    param refs: str, ref translations.
    return: {n-gram: (num_of_mached_ngrams, num_of_test_ngrams, score)}, where n-gram is 1 to ngram_max and score is 0 to 1
    '''
    tst_str=test # 'str'
    ref_str=ref
    if opt.consider_synonyms:
        closest=closest_syntest_to_ref(tst_str, ref_str)
    else:
        closest=test
    # print
    # print test
    # print closest
    # print ref
    # print
    if rare_words!=None:
        rare_words=set(rare_words)
    result={}
    for n in range(1, ngram_max+1):
        tst=ngram(tst_str, n) # ['str']
        ref=ngram(ref_str, n)
        cls=ngram(closest, n)
        if tst==None or ref==None or cls==None:
            # print n, 'is 0', [tst_str], (tst, ref, cls)
            result[n]=(0, 0, 0.0)
            continue
        tstc=Counter(tst)
        refc=Counter(ref)
        clsc=Counter(cls)
        m_all=0
        # print tst, ref, cls
        for word in clsc.keys():
            m_word=min(clsc[word], refc[word])
            if (opt.consider_synonyms) and (word in refc) and (word in clsc) and (word not in tstc):
                m_word=m_word*opt.synonym_score
            if (rare_words!=None) and (word in refc) and (word in clsc) and (len(set(word.split()) & rare_words)>0):
                m_word=m_word*opt.rare_words_score
            # print word, m_word
            m_all+=m_word
        result[n]=(m_all, len(cls), min(float(m_all)/len(cls), 1.0))
        # print '%d-gram: %0.4f'%(n, result[n])
    return result


def sbleu_corpus(test, ref):
    '''
    param test: list, [str]
    param ref: list, [str]
    return: {n-gram: score}, where n-gram is 1 to ngram_max
    '''
    assert len(test)==len(ref)
    # rare words
    if opt.consider_rare_words==True:
        rare=Counter()
        for i in ref:
            rare.update(i.split())
        rare=[i[0] for i in rare.most_common()]
        if len(rare)>opt.rare_words_min:
            rare_words=rare[-len(rare)*opt.rare_words_percent/100:]
    else:
        rare_words=None
    # sum
    ngram_list=range(1, ngram_max+1)
    test_ngrams=dict.fromkeys(ngram_list, 0)
    matched_ngrams=dict.fromkeys(ngram_list, 0)
    for t, r in itertools.izip(test, ref):
        d=sbleu(t, r, rare_words)
        for n in ngram_list:
            len_t=d[n][1]
            matched_t=d[n][0]
            test_ngrams[n]+=len_t
            matched_ngrams[n]+=matched_t
    # brevity penalty
    if opt.brevity_penalty==True:
        r=float(sum(map(len, test)))
        c=float(sum(map(len, ref)))
        penalty=exp(1-r/c) if c<r else 1.0
    else:
        penalty=1.0
    ref_length=sum([len(i.split()) for i in ref])
    len_score=min(0.0, 1.0-ref_length/test_ngrams[1])
    ind={} # individual
    cum={} # cumulative
    s=0.0
    for n in ngram_list:
        ind[n]=0.0 if test_ngrams[n]==0 else penalty*matched_ngrams[n]/test_ngrams[n]
        s+=log(ind[n])
        cum[n]=exp(s/n+len_score)
    return {'ind': ind, 'cum': cum}


def clear_str(s):
    return re.sub('[\.,-:"\'\n\?\!;\$\%]', '', s.lower())


def sbleu_file(test, ref):
    t=[clear_str(i) for i in open(test).readlines()]
    r=[clear_str(i) for i in open(ref).readlines()]
    return sbleu_corpus(t, r)


if __name__ == '__main__':
    opt, args = parse_options()

    init_sbleu(opt.synonyms_db)

    r=sbleu_file(args[0], args[1])
    print '             '+'   '.join(['%d-gram'%n for n in range(1, ngram_max+1)])
    print 'individual:  '+'   '.join(['%0.4f'%r['ind'][n] for n in range(1, ngram_max+1)])
    print 'cumulative:  '+'   '.join(['%0.4f'%r['cum'][n] for n in range(1, ngram_max+1)])
    print 'score:', '%0.4f'%r['cum'][4]


# - create all needed files from losangelestimes
# cp s/losangelestimes.en.ref.txt s/my.ref.txt ; cp s/losangelestimes.en.tst.txt s/my.tst.txt; py txt-to-seg.py ref < s/my.ref.txt > s/my.ref.seg ; py txt-to-seg.py tst < s/my.tst.txt > s/my.tst.seg; py txt-to-seg.py src `wc -l s/my.ref.txt|cut -d' ' -f1` > s/my.src.seg
# cp s/losangelestimes.en.tst.txt s/my.ref.txt ; cp s/losangelestimes.en.ref.txt s/my.tst.txt; py txt-to-seg.py ref < s/my.ref.txt > s/my.ref.seg ; py txt-to-seg.py tst < s/my.tst.txt > s/my.tst.seg; py txt-to-seg.py src `wc -l s/my.ref.txt|cut -d' ' -f1` > s/my.src.seg
# cp s/losangelestimes.en.ref.txt.back s/my.ref.txt ; cp s/losangelestimes.en.tst.txt.back s/my.tst.txt; py txt-to-seg.py ref < s/my.ref.txt > s/my.ref.seg ; py txt-to-seg.py tst < s/my.tst.txt > s/my.tst.seg; py txt-to-seg.py src `wc -l s/my.ref.txt|cut -d' ' -f1` > s/my.src.seg

# - select j lines from line i of losangelestimes and call sbleu and mteval
# j=2; for i in `seq 400 400`; do sed -n "$i,+${j}p" s/losangelestimes.en.ref.txt > s/my.ref.txt; sed -n "$i,+${j}p" s/losangelestimes.en.tst.txt > s/my.tst.txt; py txt-to-seg.py ref < s/my.ref.txt > s/my.ref.seg ; py txt-to-seg.py tst < s/my.tst.txt > s/my.tst.seg; py txt-to-seg.py src `wc -l s/my.ref.txt | cut -d' ' -f1` > s/my.src.seg; py sbleu.py s/my.tst.txt s/my.ref.txt ; ./s/mteval-v13.pl --no-smoothing -b -s s/my.src.seg -r s/my.ref.seg -t s/my.tst.seg | tail -9|head -1|cut -c -41  ; done
