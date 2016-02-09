#! encoding: u8
import sys
import time
import optparse
import traceback
import codecs
# TO UTF8
# python converter.py -i out.txt -o out1.txt --in-encoding windows-1250 --out-encoding utf-8 
# TO WINDOWS 1250
# python converter.py -i test.pl -o out.txt
ERR_LOG='err.log'
def log_error():
    '''
    log exceptions of program
    '''
    cls, obj, tb=sys.exc_info()
    lines=traceback.format_exception(cls, obj, tb)
    formatedString=time.strftime('%a %Y/%m/%d %H:%M:%S')+'\n'+''.join(lines)
    f=open(ERR_LOG, 'a')
    f.write(formatedString+'\n'+50*'-')
    f.close()

def convert(in_file, out_file, in_encoding='utf-8', out_encoding='utf-8'):
    fin= codecs.open(in_file, 'r', in_encoding, 'replace')
    fout= codecs.open(out_file, 'w', out_encoding, 'replace')
    CHUNK=1024*4
    i=0
    while True:
        in_chunk=fin.read(CHUNK)
        if not in_chunk:break
        fout.write(in_chunk)
        i+=CHUNK
        print 'CHUNCK # %s'%(i/CHUNK)
    fin.close()
    fout.close()
    
def parseOptions():
    '''
    parse program parameters
    '''
    usage='usage: %prog [options]'
    parser=optparse.OptionParser(usage=usage)
    parser.add_option('-o', '--out', dest='out_file', metavar='OUTPUT_FILE', help='input file name')
    parser.add_option('-i','--in', dest='in_file', metavar='INPUT_FILE', help='output file name')
    parser.add_option('--in-encoding', dest='in_encoding', default='utf-8', metavar='INPUT_ENCODING', help='encoding of input file(default is utf-8)')
    parser.add_option('--out-encoding', dest='out_encoding', default='windows-1250', metavar='OUTPUT_ENCODING', help='encoding of output file(default is windows-1250)')
    options, args=parser.parse_args()
    if not options.in_file:
        parser.error("input file not given")
    if not options.out_file:
        parser.error("output file not given")
    return options, args, parser

def main():
    opt, args, parser=parseOptions()
    try:
        print 'Converting ...'
        convert(opt.in_file, opt.out_file, opt.in_encoding, opt.out_encoding)
        print 'FINISHED.'
    except:
        print "!!!! error In covering text file !!!! see [%s] log file."%ERR_LOG
        log_error()
    
if __name__=='__main__':
    main()
    
