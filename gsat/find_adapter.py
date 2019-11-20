import re
import gzip
from Bio.SeqIO.QualityIO import FastqGeneralIterator

def find_a (fqfile, prefix):
    #logstring = "\tFinding adapter sequence using prefix" + prefix
    prefixcount = 0
    seqcount = 0
    aseqs = {}
    if(re.search("gz$", fqfile)):
        fqhandle = gzip.open(fqfile, "rt")
    else:
        fqhandle = open(fqfile, "rt")
    for title, seq, qual in FastqGeneralIterator(fqhandle):
        seqcount += 1
        if(seq.startswith(prefix)) :
            prefixcount += 1
            aseq = seq[len(prefix):]
            if(len(aseq) > 20) :
                aseq = aseq[0:20]
            if aseq in aseqs:
                aseqs[aseq] += 1
            else:
                aseqs[aseq] = 1
    fqhandle.close()
    #print("\t\tPrefix", prefix, "found", prefixcount, "times out of", seqcount,
      #" records.")
    bestaseq = sorted(aseqs, key=aseqs.get, reverse=True)[0]
    bestperc = round((aseqs[bestaseq] / prefixcount) * 100, 1)
    #print("\t\tMost frequent adapter (first 20nts):", bestaseq, "found", aseqs[bestaseq],
      #"times (", bestperc, '%)')
    return bestaseq 




    
            

            

        
        
