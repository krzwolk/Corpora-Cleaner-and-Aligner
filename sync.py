from pprint import pprint
from translate import GoogleTranslator
from config import *
from crawltranslator.Manager import runapp
import multiprocessing
import time

class Buffer(object):
    def __init__(self, f, buffLen, negFactor):
        # f:file object,
        # buffLen: initial buffer length
        # negFactor: misplaced decrease factor
        self.f=f
        self.index=0
        self.negFactor=negFactor
        self.buffLen=buffLen
        # buffer of lines that are read from file
        self.buffer=[]
        # used for counting misplaced and correct placed lines
        self.misplaced=0
        self.correctpalced=0
        # dict to count number of visits of each line in buffer to remove after remove limit exceeds.
        self.negRates={}
        # init buffer 
        for i in range(buffLen):
            newLine=self.f.readline()
            self.buffer.extend(sentencesOf(newLine))
    def chooseLike(self, lines, comparefn, factor):
        global MIS_ALIGNED, ALIGNED
        matrix=[]
        for i, line in enumerate(lines):
            rates=[comparefn(line, bufferLine)-abs(j-i-self.index)*(self.negFactor*factor) for j, bufferLine in enumerate(self.buffer)]
            matrix.append(rates)
        indexes=range(len(self.buffer))
        indexes.sort(lambda a, b: 1 if matrix[0][a]<matrix[0][b] else -1)
        for index in indexes:
            l=[matrix[i][index] for i in range(len(matrix))]
            for i, rate in enumerate(l[1:]):
                if rate>l[0]: break
            else:
                rate=matrix[0][index]
                maxRateIndex=index
                selectedLine=self.buffer[maxRateIndex]
                break
        else:
            selectedLine=''
            rate=0
            maxRateIndex=-1
        if rate>=factor:
            self.buffer.pop(maxRateIndex)
            if self.index!=maxRateIndex: self.misplaced+=1
            else: self.correctpalced+=1
            self.index=maxRateIndex
        while len(self.buffer)<self.buffLen:
            newLine=self.f.readline()
            if newLine=='': break
            self.buffer.extend(sentencesOf(newLine))
        for i in range(self.index):
            if self.buffer[i] not in self.negRates: self.negRates[self.buffer[i]]=0
            self.negRates[self.buffer[i]]+=1
            if self.negRates[self.buffer[i]]>self.buffLen: self.buffer[i]=None
        print(len(self.buffer), self.index)
        self.index-=self.buffer.count(None)
        while self.buffer.count(None)>0: self.buffer.remove(None)
        return selectedLine, rate
        
        
class FileReader(object):
    def __init__(self, f, buffLen):
        self.f=f
        self.buffLen=buffLen
        self.buffer=[]
        self.i=0
        for i in range(self.buffLen):
            self.buffer.append(self.f.readline())
    def next(self):
        self.i+=1
        first=self.buffer.pop(0)
        self.buffer.append(self.f.readline())
        return first

def mycapitalize(s):
    if 'a'<=s[0]<='z': s=s[0].upper()+s[1:]
    return s
def sentencesOf(line):
    line=line.strip()
    if not (line.endswith('.') or line.endswith('?') or line.endswith('!')): line=line+'.'
    # find distinct sentences of one line.
    l=re.findall('[^.!?]+[.!?]',line)
    sentences=[mycapitalize(sentence.strip()) for sentence in l if sentence.strip()!='']
    ret=[]
    for sentence in sentences:
        if len(ret)==0 or ret[-1]!=sentence: ret.append(sentence)
    return ret
def removeDuplicates(line):
    line=line.strip()
    if not (line.endswith('.') or line.endswith('?') or line.endswith('!')): line=line+'.'
    l=re.findall('[^.!?]+[.!?]',line)
    sentences=[mycapitalize(sentence.strip()) for sentence in l if sentence.strip()!='']
    ret=[]
    for sentence in sentences:
        if len(ret)==0 or ret[-1]!=sentence: ret.append(sentence)
    # assert ' '.join(ret).strip()!='', line
    return ' '.join(ret)
def sync():
    print('Making outputs ...')
    # intermediate file is translation of before.pl in english with google translator
    f1=FileReader(open(BEFORE_INTER), BEFORE_INTER_BUFFER_LENGTH)
    f2=FileReader(open(BEFORE_PL), BEFORE_INTER_BUFFER_LENGTH)
    f3=Buffer(f=open(BEFORE_EN), buffLen=BEFORE_EN_BUFFER_LENGTH, negFactor=NEG_FACTOR)

    fw1=open('after-me.en', 'w')
    fw3=open('after-me.pl', 'w')
    # count lines that are used from before.inter and lines which are empty
    inter_used=emptyLines=0
    while True:
        poor_trans = False
        line1=f1.next()
        line2=f2.next()
        # end of polish and intermediate english files. Empty lines has \n at least
        if line1=='':  break
        # bypass empty lines
        if line1.strip()=='':
            emptyLines+=1
            continue
        print('line: %d'%(f1.i))                        
        # it seams, it is better that polish lines do not be splited.
        if len(line1)>SPLITE_LENGTH:
            lines1=sentencesOf(line1)
            lines2=sentencesOf(line2)
            if len(lines1)!=len(lines2):
                lines1=[removeDuplicates(line1)]
                lines2=[removeDuplicates(line2)]
        else:
            lines1=[removeDuplicates(line1)]
            lines2=[removeDuplicates(line2)]
        for i in range(len(lines1)):
            print('%s: %s'%('before.inter', lines1[i].strip()))
            for comparefn, factor in COMPARATORS:
                line3, score=f3.chooseLike(lines1[i:]+f1.buffer, comparefn, factor)
                print('fn: %s, score: %s, factor: %s'%(comparefn.__name__, round(score, 2), factor))
                if score>=factor:
                    print('%s: %s'%('before.en', line3.strip()))
                    fw1.write(line3.strip()+'\n')
                    break
            else:
                inter_used+=1
                poor_trans = True
                print('before.inter selected!')
                if not DELETE_ON_POOR_TRANSLATION:
                    fw1.write(lines1[i].strip()+'\n')
            if not (poor_trans and DELETE_ON_POOR_TRANSLATION):
                fw3.write(lines2[i].strip()+'\n')
            print('*********************************************')
    print('Finished successfuly.\nAligned: %s, Misaligned: %s, Google: %s, Empty: %s'%(f3.correctpalced, f3.misplaced, inter_used, emptyLines))
    fw1.close()
    fw3.close()
    f1.f.close()
    f2.f.close()
    f3.f.close()

def makeInterFree():
    l = multiprocessing.Event()
    s = multiprocessing.Event()
    t = multiprocessing.Process(name='Translator', target=runapp, args=(l, s))
    t.start()
    l.set() #Loading
    time.sleep(30)
    s.set() #Starting
    t.join()
    
def makeInter():
    print('Translating')
    print('Please wait ...')
    f1=open(BEFORE_PL)
    f2=open(BEFORE_INTER, 'wb')
    translator=GoogleTranslator()
    i=0
    for line in f1:
        print('line %d translated.'%i)
        i+=1
        if line.strip()!='': 
            if len(line)>1500: lines=sentencesOf(line)
            else: lines=[line]
            for line in lines:
                translated=translator.translate(line, source='pl')
                # assert len(translated)==1, (line, translated)
                f2.write(translated[0]['translatedText'].encode('u8').replace('&#39;', '\''))
            f2.write('\n')
        else:
            f2.write('\n')
        
    f1.close()
    f2.close()
    print('Translating finished successfuly')
        
        
if __name__=='__main__':
    if not DISABLE_TRANSLATION:
        if FREE_TRANS: makeInterFree()
        else: makeInter()
    sync()
    
