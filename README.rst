About
=====

This project was about alignment of misplaced English translation of Polish sentences into segment aligned corpora files. As input program receives 2 files. First has Polish text and second has it’s translation into English. In both files a single line should represent one sentence pair. Approximately each Polish file line has a corresponding line for its translation in English file. But some translation lines are sometimes misplaced. Also some lines has no translation and some English file lines are translation of no correspondence to line in Polish file. Also other problems can occur. There was a need for a script to find translation of each Polish line and put it in its correct place in English file. The idea was to use Google Translation API for lines that their translation do not exist in English file and for comparisons between those two files. Firstly there is a need for our script to make an English translation file that has each line of translation corresponding to lines in Polish file. It means we need translation of first line of Polish file in first line of English file and second one in second and so on. Than we compare newly translated English file with original English file, both line by line and also scan neighbor lines. If we find translation in English that similar by some factor we use original line, and if we do not we use Google’s translation.
Our strategy to find correct translation of each Polish line is getting help from Google’s translator. We translate all lines of Polish file with Google translator and put each line
translation in intermediate English translation file. This intermediate translation helps us
find the correct line in English translation file and put it in its correct position. Let’s
call Polish file before.pl, translation file before.en and Google translated file before.inter. We use similarity of each before.inter line with lines in before.en to find what line in before.en is translation of what line in before.pl. This script should do this in following steps:
1. Choose first line of before.inter and first line of before.pl;
2. Compare this before.inter line with for example 3 first lines of before.en;
3. Choose most similar line in these 3 tests from before.en;
4. If selected line similarity rate is more than specific acceptance rate, choose it as translation of corresponding before.pl line;
5. If selected line similarity rate in not high enough ignore it and select before.inter line for translation;
Of course actual solution is more complicated. Suppose we choose one of lines of before.en as most similar line to specific before.inter line and it’s similarity rate is high enough to be accepted as translation. But this line can be more similar to next line of before.inter and similarity rate of this selected line and next line of before.inter is higher. For ex.
Before.inter Before.en Similarity rate

I go to school every day. I like going to school every day. 0.6
I do not go to school every day. 0.7
We will go tomorrow. 0.3
I don’t go to school every day. I like going to school every day. 0.55
I do not go to school every day. 0.95
We will go tomorrow. 0.3
In such situations, we should select “I do not go to school every day.” from Before.en instead of “I don’t go to school every day” from Before.inter not for “I go to school every day.”. So we should consider similarity of selected line with next lines of before.inter to make the best possible results in alignment process.
But this is not most important problem that makes this script more complicated. Comparing before.inter lines with before.en lines is not easy work, and it becomes harder when we want to use similarity rate to choose correct translation to use in real world.
We can have many strategies to compare two sentences. We can split each sentence to its words and find number of words which are in both sentences. But this approach has some problems. For example we want compare “It is origami.” to these sentences:
– The common theme what makes it origami is folding is how we create the form.
– This is origami.
With this strategy, first sentence is more similar because has all 3 words “it”, “is” and “origami”. But it is clear that second sentence is correct choice.
We can solve this problem by dividing number of words in both sentences by number of total words of both sentences. But this approach has some other problems too. There are words that are used very commonly in most sentences, like “am”, “is”, “are”, etc.
Sometimes counting these words in intersection of sentences causes that our rating results becomes wrong. We call these words stop words. So we should remove these words before comparing two sentences.
Another problem is that sometimes we find for example “boy” in one sentence and have “boys” in other sentence. Despite this fact that these two shapes should be counted as similarity of two sentences, but with this strategy these words are not counted.
Next problem is that place of words in sentences is not effective in comparing when we are just counting. In Python there are other ways for comparing Strings that are better than counting intersection length and solve these two problems.
Python has a “difflib” library for string comparison. This library has a function to compare 2 strings. This function first finds matching blocks of two strings. For example in „abxcd”, „abcd” we can use difflib to find matching blocks.
>>> s = difflib.SequenceMatcher(None, „abxcd”, „abcd”)
>>> s.get_matching_blocks()
[Match(a=0, b=0, size=2), Match(a=3, b=2, size=2), Match(a=5, b=4, size=0)]
Difflib’s compare function which is called “ratio”, divides length of matching blocks by length of two strings and return a number between 0 and 1. From documentation of ratio function is simply called ratio() and it returns a measure of the sequences’ similarity as a float value in the range [0, 1].
Where T is the total number of elements in both sequences, and M is the number of matches, this is 2.0*M / T. Note that this is 1.0 if the sequences are identical, and 0.0 if they have nothing in common.
Using this commonly used function to compare strings instead of counting similar words, help us to solve problem of similarity of “boy” and “boys” and the problem of considering position of words in sentences.
Other problem in comparing lines are synonyms. For example in these sentences:

I will call you tomorrow.
I would call you tomorrow.

If we want to know if these sentences are the same, we should know that will and would can be used instead of each other.
We used python module called NLTK and WordNet® which is a large lexical database of English to find synonyms of each word and use these synonyms in comparing sentences. With synonyms of each word we make multiple sentences from each sentence.
For example suppose that “game” that has synonyms list “play”, “sport”, “fun”, “gaming”, “action”, “skittle”. If we use for example sentence of “I do not like game.” We make these sentences like this:

I do not like play.
I do not like sport.
I do not like fun.
I do not like gaming.
I do not like action.
I do not like skittle.

And then we try to find best rate from comparing all these sentences instead of just comparing main sentence. One problem in this situation is that this type of comparing take too long time. Because for each selection we need to do tons of comparisons.
Difflib has 2 other functions to compare strings that are faster than ratio but their accuracy is worse. They can be choose in config file as well. In real word to overcome all these problems and get best results, we have two criteria to consider. One of them is speed of comparison function and other one is acceptance rate for comparison functions.
To have best results our script provides this ability to user to have multiple functions with multiple acceptance rates. Fast functions with lower quality of result is tested at first. If they can find results with very high acceptance rate, we accept their selection. If acceptance rate is not enough, we can go to best quality functions that are slower to find correct selection. User can configure these rates manually and test outcome quality to get best results.
Because we used Google Translator API and comparison function that are not specific to any language the program should be able to help in alignment of any language pairs with English that are supported by Google Translator. Alignment between pair without English language would require to use different lexical library for synonyms or not using some comparison functions.
Since Google API is quite expensive we implemented also free solution based on web crawling on 3 services like Google Translator, Bing Tranlsator, and Babylon. It is possible to use single of them or all of them simulatusly for better performance – but still this solution is much slower that one by Google API and can lead to worse results espacially when using many different translation engines at the same time. This solution is onl for educational purposes.
The crawler translator was developed to feed the native sentences to online translation services such as Google, Bing, and Babylon and retrieve the translated text. These online services have their own web sites for serving human users. Thus the problem was how to simulate the behavior of human user when entering the source texts. On the other hand, since there was the potential of being blocked by the online services if the program overloadeds the online services, there should be enough delay in feeding the sentences.
The crawler translator was developed using Python programming language, PyQt graphical user interface, and PyQt webkit for implementing a simple web browser. The webkits are frameworks for handling the web pages within the programming languages. A simple GUI based on the data provided in the config file, loads the web pages of online translation services. These pages are loaded in separate windows and work in parallel. This will increase the speed of the translation.
The main part of the module is a manager which controls the translators (browsers), input file reader and the output file writer. The manager holds a queue for buffering the lines of the input file. When the queue is loaded with a bunch of the input lines, the translators wakes up and starts translating the texts. After retrieving the translated texts, the result will be put into the output queue which after
some iterations will be written in the output file. Since the translators are Python threads, the events and queue block mechanism are used to do the signaling between the producer (input file queue) and the translators (browsers). Since the input files might be big, an input queue with synchronization capability is used. This queue is loaded with some lines of the input file specified in the config file and waits until all the lines are consumed by the translators. The model of the program is a kind of consumer producer. One input producer and many consumers (translators). Each translator will try for some time to retrieve the translation, but if it faces with a time out,
a dummy string will be returned. This dummy string can be configured in the config file. Also the number of trials is configurable in the config file.
Upon startup, the program waits for some time (specified in the config file) so that the browsers get loaded with the pages. The feeding and retrieving operation is done via some small javascript codes. Thanks to AJAX, whenever the text is put into the input box of the online services, they start requesting the translation. So after a while the translator checks for the results. You can see the structure of the program in the following diagram.
 
 
The Manager.py file contains three classes: MdiBrowser, MainWindow, and Manager. The
MdiBrowser and MainWindow are GUI classes responsible for making the main window, menu, and browser windows. These classes are based on Qt library widgets and frames. There has been defined two actions for loading and starting the translation process. The Manager class is the controller of the program. It is derived from the Thread python
standard class and is executed as a background daemon. It holds the following objects:

1. InputQueue: The synchronized queue data structure for loading the input texts. In fact it is a wrapper class for Queue object defined in the standard library of python. Since the control of the input queue should be unblocking, it is also a running thread. A FileReader class also helps the InputQueue for reading lines from input file. In each iteration, the InputQueue main loop waits for the queue to get empty. As it is noted before, the translator threads (described later) consumes the texts from the InputQueue. The number of lines read in each iteration is specified in the config file (INPUT_FILE_CHUNK). A callback function is passed to the input queue
manger that is called when the lines are consumed and so the manager writes down the
translated lines.

2. OutputQueue: The output queue is responsible for holding the translated lines. The translators store their result in the output queue of the manager. In each iteration the translated lines are saved in the output file by the output queue object specified in the config file.

3. Translator: Manager instantiates some objects from the Translator class for doing the translation process concurrently. The Translator is derived from the Thread class. The translators are active in background. When the manager object is started by the MainWindow action, i.e. start, the ‚run’ function of the Manager is started. In this function the translators are created and started as a thread:
for server in services:
for id in range(services[server][1]):
browser = self.maingui.getBrowser(server, id)
parser = ServiceParser.UIParser(self.maingui.getBrowser(server, id))
self.createTranslator(parser).start() #Startup of the translators
The run method of the translator object is responsible for feeding and retrieving the translated text from the browsers:
while self.cont:
chunk = self.getChunk() #chunk number and sentences
prn(‚Feeding: ‚+`chunk[0]`+’ ‚+chunk[1].encode(‚u8’))
translated = self.service.feedChunk(chunk)
self.outputQueue.putChunk(chunk[0], translated)
self.inputQueue.task_done()
When the translator consumes a chunk it informs the input queue by calling the task_done
method. The translator object has two internal objects for communicating with the online
services such as Google or Bing; UIParser and MdiBrowser.

3.1. MdiBrowser: This class is responsible for loading the web page and the strings are fed directly to this object. The setInput is implemented for feeding process. After loading the input buffer the _setInput function is executed:
def _setInput(self):
if self.server == ‚Google’:
self.getIControl().setPlainText(self.input)
elif self.server == ‚Bing’:
js = „Default.SourceValue.set(‚%s’)” % self.input
self.page().mainFrame().evaluateJavaScript(js)
elif self.server == ‚Babylon’:
js = „GEBI(‚source’).textContent = \”%s\”; setCookie(‚global’,’stop’);
setCookie(‚showADV’, -1000); setCookie(‚sprovider’,’babylon’);
Provider(‚babylon’);” % self.input
self.page().mainFrame().evaluateJavaScript(js)
These commands notify the online service about the arrival of the new string. The _setInput function is executed by the set input action defined in each browser. Next step is to check for the translated text; this is done by the _getInput function:
def _getOutput(self):
if self.server == ‚Google’:
out = self.getOControl()
result = ”
result += str(out.toPlainText().toUtf8())
self.output = result
elif self.server == ‚Bing’:
js = „Default.OutputValue.get()”
outjs = self.page().mainFrame().evaluateJavaScript(js)
self.output = str(outjs.toString().toUtf8())
elif self.server == ‚Babylon’:
js = „parent.GEBI(‚target’).value”
outjs = self.page().mainFrame().evaluateJavaScript(js)
self.output = str(outjs.toString().toUtf8())
As it can be seen there is detailed check for each Google, Bing and Babylon; since their web sites are different in the way of handling the data we had to hard code the commands. The commands are mostly javascript code snippets. In addition the check for arriving the translated text is complicated to some extent and it is covered in the UIParser class described in the next section.
3.2. UIParser: This class is an interface between the translator and the browser. Its main function, feedChunk, sends the text to the browser and waits for arrival of the translation. The procedure for checking of the arrival is a little complicated and is tailored for each online service separately. There are three main if/elif blocks in the feedChunk that check for the translated text. The conditions are different and the maximum trial for checking is specified in the config file (MAX_CHECK_TRIAL). If the translated text is not detected within the trials
specified, a dummy string (TIMEOUT_TRANSLATION_STR) is returned.
def feedChunk(self, chunk):
…
if self.browser.server == ‚Google’:
while iter < config.MAX_CHECK_TRIAL:
…
elif self.browser.server == ‚Babylon’:
while iter < config.MAX_CHECK_TRIAL:
…
elif self.browser.server == ‚Bing’:
while iter < config.MAX_CHECK_TRIAL:
…

Finally some extra scoring algorithms were implemented into the program. Those are more suited for comparing language translation quality. Those are of most important part of our aligner which are used to compare sentences and find matching sentence in aligning process. In this part of project we added some new algorithms to our scoring algorithms list.
Machine translation evaluation is known context with many known solutions that we can use to make our aligner scoring system work better. Evaluating the quality of a computer-generated translation relative to a human-generated reference translation or set of human-generated reference translations is useful for automatic parameter tuning, to compare the quality of two machine translation systems, and to carry out minimum Bayes risk decoding. But we use these algorithms here to have scores of likeness of two sentences to choose correct one in aligning process.
We added BLEU (Bilingual Evaluation Understudy), TER (native implementation) and CER (character edit rate; native implemtation) by using pycdec and RIBES (Rank-based Intuitive Bilingual Evaluation Measure).
We used here cdec and pycdec. cdec is a decoder, aligner, and learning framework for statistical machine translation and similar structured prediction models.
– Translation and alignment modeling based on finite-state transducers and synchronous context-free grammars.
– Implementations of several parameter learning algorithms.
– Fast, extensible C++ implementation and Python interface (pycdec).
– Modular architecture that separates search space construction, rescoring, and inference.
pycdec is a Python module for the cdec decoder. It enables Python coders to use cdec’s fast C++ implementation of core finite-state and context-free inference algorithms for decoding and alignment. The high-level interface allows developers to build integrated MT applications that take advantage of the rich Python ecosystem without sacrificing computational performance.
cdec includes implementations of basic evaluation metrics (BLEU, TER and CER), exposed in Python via the cdec.score module. For a given (reference, hypothesis) pair, sufficient statistics vectors (SufficientStats) can be computed. These vectors are then added together for all sentences in the corpus and the final result is finally converted into a real-valued score.
Writing a script which computes the BLEU score for a set of hypotheses and references is thus straightforward:
import cdec.score
with open(‚hyp.txt’) as hyp, open(‚ref.txt’) as ref:
stats = sum(cdec.score.BLEU(r).evaluate(h) for h, r in zip(hyp, ref))
print(‚BLEU = {0:.1f}’.format(stats.score * 100))
Multiple references can be used by supplying a list of strings instead of a single string:
cdec.score.BLEU([r1, r2])


To install cdec and pycdec follow these steps:
$sudo apt-get install autoconf
$sudo apt-get install libtool
$sudo apt-get install flex
$sudo apt-get install libboost-all-dev
$wget https://github.com/redpony/cdec/archive/master.zip
$unzip master.zip
in cdec-master directory:
$autoreconf -ifv
$./configure
$make
in cdec-master/python directory
$sudo python setup.py install


RIBES (Rank-based Intuitive Bilingual Evaluation Measure) is an automatic evaluation metric for machine translation, developed in NTT Communication Science Labs. Website: http://www.kecl.ntt.co.jp/icl/lirg/ribes/
You can check all scoring algorithms results for pair of sentences by editing comparators.py. For this purpose you must open this file and go to end of file and change s1 and s2 to sentences which you want.
s1=’It is just a small test’
s2=’It is just another small test’
Then run:
$python comparators.py
It outputs result of all scoring functions in something like this:
(‚cmp_BLEU’, 0.4889230400275687)
(‚cmp_CER’, 0.8260869565217391)
(‚cmp_SSK’, 0.78568035364151)
(‚cmp_TER’, 0.8333333333333334)
(‚cmp_RIBES’, 0.9827590514957919)
(‚cmp_sequence’, 0.92)
(‚cmp_sequence_stopwords’, 1.0)
(‚cmp_set’, 0.5)
(‚cmp_sequence_synonyms_quick’, 1.0)
(‚cmp_sequence_synonyms’, 1.0)
(‚cmp_sequence_synonyms_2D’, 1.0)
Scoring algorithms can be configured by ordering execution and it’s acceptance rates. This can be done by changing COMPARATORS variable in config.py
COMPARATORS=[
(cmp_BLEU, 0.3),
(cmp_CER, 0.6),
(cmp_SSK, 0.6),
(cmp_TER, 0.6),
(cmp_RIBES, 0.8),
(cmp_sequence, .7),
#(cmp_sequence_stopwords, .6),
#(cmp_set, .6),
(cmp_sequence_synonyms_quick, .6),
(cmp_sequence_synonyms, .3)
#(cmp_sequence_synonyms_2D, .3)
]

You can disable/enable each algorithm by adding/removing # character at beginning of line. Algorithms that are first, would be executed first, and if we can find a sentence that it’s score is more than the number that is written in front of algorithm, we would not continue to next algorithms. But if none of sentences can reach this score, we continue to next algorithm. So order of execution and acceptance rate of each algorithm is very important to configure aligner do best.




USAGE CONFIGURATION INSTALLATION
=====
Remember to get working Google API Key ! If you are very patient man you can manually translate (for free) and create file before.inter with translate.google.com page. It can translate at once about 200 semi-long sentences.
NOTE ! There is no best cofiguration – everything depends on data to be aligned. You are supposed to take sample 1000 lines example a try to determine the best coparison fuctions with scoring thereshols with trial and error method.
Let before.pl and before.en be parallel corpora of Polish and English sentences that are not aligned too good. We will call before.inter a file that will be obtained by translating before.pl to English manually or witch the use of Google Translator API.
Program requires Python-nltk library and WorldNet for synonyms.
Most important configuration is to be done in config.py file.
Firstly program used similarity comparison based on words. SUM(Intersection of before.en and before.inter)/SUM(Union of before.en and before.inter). Results were not good enough for ex. go and goes were treated as totally different words.
Current version has many comparison functions.
difflib.Sequencematcher that is a flexible class for comparing pairs of sequences of any type, so long as the sequence elements are hashable is used for comparisons.
The basic idea is to find the longest contiguous matching subsequence that contains no „junk” elements. The same idea is then applied recursively to the pieces of the sequences to the left and to the right of the matching subsequence. This does not yield minimal edit sequences, but does tend to yield matches that „look right” to people. SequenceMatcher tries to compute a „human-friendly diff” between two sequences. Unlike e.g. UNIX(tm) diff, the fundamental notion is the longest *contiguous* & junk-free matching subsequence. That’s what catches peoples’ eyes.
Depending on comparison function for each word in a sentence a sorted list of synonyms is generated. With that a lot of potential sentences are generated with every possible synonym. Also not important words from sentences are being removed.
For ex.
I go to school.
We remove „I” and „to” as not important and remaining part is:
Go school
Now we generate any possible combination:
go school
went school
go back school
go class
went class
etc.
Each such sentence is compared to original file. Best match is chosen with cmp_sequence_synonyms function. It is also possible to make 2D comparison set. Program generates sentences in the same manner for sentences in before.inter and before.en and compares each other witch cmp_sequence_synonyms_2D function.
There are 6 comparison functions for you disposal. Remember that for different kinds of data different functions and parameters must be chooses for best results. We recommend to evaluate results on small let’s say 2000 lines corpora.
Comparators arranged by execution order with each one factor rate
cmp_sequence: it just uses python difflib comparison ratio
cmp_sequence_stopwords: it first removes stop words and then use python difflib comparation ratio
cmp_set: it divides length of intersection of words in two lines by union of words of two lines.
cmp_sequence_synonyms_quick: it compares all shapes of sentence 1 with sentence 2 with difflib quick comparison ratio
cmp_sequence_synonyms: it compares all shapes of sentence 1 with sentence 2 with difflib comparison ratio
cmp_sequence_synonyms_2D: it compares all shapes of sentence 1 with all shapes of sentence 2 with difflib very quick comparison ratio
(cmp_sequence, .8), where .8 is acceptance rate, choose values between 0 and 1
(cmp_sequence_stopwords, .6),
(cmp_set, .6),
(cmp_sequence_synonyms_quick, .6),
(cmp_sequence_synonyms, .3)
(cmp_sequence_synonyms_2D, .3)
Increasing acceptance rate cause script to use more from Google translation, and decreasing cause script to have more mistakes in aligning.
If a corresponding line did not match acceptance rate program checks if any neighbor lines might be right translations (depending on size of buffer). The same happens if program finds empty line in target language file. If no good enough translations can be found a translation from Google Translator is used.
********************************************************

1. How use this script?
Put before.en and before.pl in directory when sync.py resides and then run
$python sync.py
in console. This script will make 2 synced files named after-me.en and after-me.pl in directory.
********************************************************

2. How enable and disable automatic translation?
you can set variable DISABLE_TRANSLATION to True or False to disable or enable automatic translation. If you want to disable automatic
translation, you should make before.inter file manually by translating before.pl from Google translator web site or any similar.
********************************************************

3. How install and configure nltk and WorldNet?
run
$sudo easy_install nltk
When installation finished, run python in console and write:
$ python
>>> import ntlk
>>> nltk.download()
when you run this command, a window will appear. Go to Corpora tab and select WorldNet from column identifier. Then press download button
and wait until downloading finished.
********************************************************

4. How rename outputs or inputs?
You can config output and input file names from config file.

Final info
====

Feel free to use this tool if you cite:
Wołk K., Marasek K., “A Sentence Meaning Based Alignment Method for Parallel Text Corpora Preparation.”, Advances in Intelligent Systems and Computing volume 275, p.107-114, Publisher: Springer, ISSN 2194-5357, ISBN 978-3-319-05950-1

For more information, see: http://arxiv.org/pdf/1509.09093

For any questions:
| Krzysztof Wolk
| krzysztof@wolk.pl
