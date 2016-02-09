# google translation api key
API_KEY=''

# stop words
STOP_WORDS=['i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves', 'you', 'your', 'yours', 'yourself', 'yourselves', 'he', 'him', 'his', 'himself', 'she', 'her', 'hers', 'herself', 'it', 'its', 'itself', 'they', 'them', 'their', 'theirs', 'themselves', 'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those', 'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing', 'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as', 'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about', 'against', 'between', 'into', 'through', 'during', 'before', 'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in', 'out', 'on', 'off', 'over', 'under', 'again', 'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why', 'how', 'all', 'any', 'both', 'each', 'few', 'more', 'most', 'other', 'some', 'such', 'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very', 's', 't', 'can', 'will', 'just', 'don', 'should', 'now']

# input and output file names
BEFORE_PL='before.pl'
BEFORE_INTER='before.inter'
BEFORE_EN='before.en'
AFTER_EN='after-me.en'
AFTER_PL='after-me.pl'

# If there is no good translation and this flag is set to True, no results will
# be written to after_en and after_pl, otherwise translation will be selected
# from before_inter
DELETE_ON_POOR_TRANSLATION = True

# use this variable to configure length of intermediate lines that cause convert lines to sentences.
# if you want all lines be breaked to sentences set this to 0
# lines longger than this variable become splitted into sentences.
SPLITE_LENGTH=400

# disable translation
DISABLE_TRANSLATION=True

# LENGTH OF BUFFER SETNTENCES norlamnie 4 gdy robimy aligner gdy fitr to 1
BEFORE_INTER_BUFFER_LENGTH=1
BEFORE_EN_BUFFER_LENGTH=1

# when we select line from before.en that has distance in position with current line in before.inter,
# we decrease score by this factor of desiered score.
NEG_FACTOR=.1

# comparators arranged by execution order wtih each one factor rate
# cmp_BLEU, cmp_CER, cmp_SSK, cmp_TER: algorithm implementation at https://github.com/redpony/cdec
# cmp_RIBES: RIBES algorithm implementation at http://www.kecl.ntt.co.jp/icl/lirg/ribes/
# cmp_sequence: it just uses python difflib comparation ratio
# cmp_sequence_stopwords: it first removes stop words and then use python difflib comparation ratio
# cmp_set: it devides length of intersection of words in two lines by union of words of two lines.
# cmp_sequence_synonyms_quick: it compares all shapes of sentence 1 with sentence 2 with difflib quick comparation ratio
# cmp_sequence_synonyms: it compares all shapes of sentence 1 with sentence 2 with difflib comparation ratio
# cmp_sequence_synonyms_2D: it compares all shapes of sentence 1 with all shapes of sentence 2 with difflib very quick comparation ratio

# sbleu config
SBLEU_NGRAM = 2
# end - sbleu config

from comparators import *
COMPARATORS=[
   (cmp_BLEU, 0.3),
   (cmp_CER, 0.2),
   (cmp_SSK, 0.6),
   (cmp_TER, 0.8),
   (cmp_RIBES, 0.9),
   (cmp_SBLEU, 0.8),
   (cmp_sequence, .3),
   (cmp_sequence_stopwords, .4),
   (cmp_set, .1),
   (cmp_sequence_synonyms_quick, .8),
    (cmp_sequence_synonyms, .8)
   # (cmp_sequence_synonyms_2D, .3)
]

# enable free translation
FREE_TRANS=True
