import os
import re
import gzip
from Bio.SeqIO.QualityIO import FastqGeneralIterator

def trim_adapter (fqfile, adapter, odir):
    #print("\tTrimming adpaters using sequence", adapter)

    if(re.search(r'\.gz$', fqfile)):
        trimfile = re.sub(r'\.gz$', '.trimmed.gz', fqfile)
        fqhandle = gzip.open(fqfile, "rt")
        outhandle = gzip.open(trimfile, "wt")
        ioutfile = re.sub(r'\.gz$', '.triminfo.csv', fqfile)
        iouthandle = open(ioutfile, "wt")
    else:
        trimfile = fqfile + '.trimmed'
        fqhandle = open(fqfile, "rt")
        outhandle = open(trimfile, "wt")
        ioutfile = fqfile + '.triminfo.csv'
        iouthandle = open(ioutfile, "wt")

    # Check on triminfo.csv file and initiate if necessary
    #ioutfile = odir.strip("/") + '/triminfo.csv'
    #if os.path.exists(ioutfile):
        #iouthandle = open(ioutfile, "at")
    #else:
        #iouthandle = open(ioutfile, "wt")
        #iouthandle.write("sample,category,count\n")
        
    incount = 0
    okcount = 0
    shortcount = 0
    nocount = 0
    zerocount = 0
    for title, seq, qual in FastqGeneralIterator(fqhandle):
        incount += 1
        offset = seq.find(adapter)
        if(offset < 0):
            nocount += 1
        elif(offset == 0):
            zerocount += 1
        elif(offset < 6):
            shortcount += 1
        else:
            okcount += 1
            tseq = seq[0:offset]
            tqual = qual[0:offset]
            outhandle.write("@{0}\n{1}\n+\n{2}\n".format(title, tseq, tqual))
    fqhandle.close()
    outhandle.close()
    #print("\t\tInput:", incount)
    okperc = round((okcount / incount) * 100, 1)
    noperc = round((nocount / incount) * 100, 1)
    zeroperc = round((zerocount / incount) * 100, 1)
    shortperc = round((shortcount / incount) * 100, 1)
    okperc = round((okcount / incount) * 100, 1)
    #print("\t\tNo adapter:", nocount, "(", noperc, "%)")
    #print("\t\tEmpty (no insert):", zerocount, "(", zeroperc, "%)")
    #print("\t\tToo short (1-5nts):", shortcount, "(", shortperc, "%)")
    #print("\t\tSuccessfully trimmed:", okcount, "(", okperc, "%)")
    #print("\t\tTrimmed file:",trimfile)

    # reporting to informational csv file
    left_clean = re.sub('^.*\/', '', fqfile)
    sample_clean = re.sub('\.fq.*$|\.fastq.*$', '', left_clean)
    # strip file name to base name for the sample
    
    #iouthandle.write("{0},Input,{1}\n".format(sample_clean, incount))
    iouthandle.write("{0},noAdapter,{1}\n".format(sample_clean, nocount))
    iouthandle.write("{0},noInsert,{1}\n".format(sample_clean, zerocount))   
    iouthandle.write("{0},tooShort1-5,{1}\n".format(sample_clean, shortcount))
    iouthandle.write("{0},Output,{1}\n".format(sample_clean, okcount))
    iouthandle.close()
    
    return trimfile


        
