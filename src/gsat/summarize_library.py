import os
import re
import gzip
from Bio.SeqIO.QualityIO import FastqGeneralIterator

def extract_reads (fqfile, odir):
    #print("\tExtracting counts")
    if(re.search(r'\.gz$', fqfile)):
        fqhandle = gzip.open(fqfile, "rt")
        outfile = re.sub(r'\.gz', '.counts.csv', fqfile)
        ioutfile = re.sub(r'\.gz', '.libinfo.csv', fqfile)
    else:
        fqhandle = open(fqfile, "rt")
        outfile = fqfile + '.counts.csv'
        ioutfile = fqfile + '.libinfo.csv'

    outhandle = open(outfile, "wt")
    iouthandle = open(ioutfile, "wt")
    reads = {}
    readcount = 0
    for title, seq, qual in FastqGeneralIterator(fqhandle):
        readcount += 1
        rnaseq = seq.replace('T', 'U')
        rnaseq = rnaseq.replace('t', 'u')
        if rnaseq in reads:
            reads[rnaseq] += 1
        else:
            reads[rnaseq] = 1
    
    uniques = 0

    # summary csv file.
    #ioutfile = odir.strip("/") + '/libinfo.csv'
    #if os.path.exists(ioutfile):
        #iouthandle = open(ioutfile, "at")
    #else:
        #iouthandle = open(ioutfile, "wt")
        #iouthandle.write("sample,countType,size,firstBase,count\n")

    left_clean = re.sub('^.*\/', '', fqfile)
    sample_clean = re.sub('\.fq.*$|\.fastq.*$', '', left_clean)
    
    abun_count = {}
    uniq_count = {}
    max_size = 0
    min_size = 1000000
    for k in reads.keys():
        uniques += 1
        outhandle.write(k + ',' + str(reads[k]) + "\n")
        key = k[0] + str(len(k))
        if key in abun_count:
            abun_count[key] += reads[k]
            uniq_count[key] += 1
        else:
            abun_count[key] = reads[k]
            uniq_count[key] = 1
        this_size = len(k)
        if this_size > max_size:
            max_size = this_size
        if this_size < min_size:
            min_size = this_size
        
    fqhandle.close()
    outhandle.close()
    #print("\t\t", readcount, "reads")
    #print("\t\t", uniques, "unique sequences")
    #print("\t\tCounts file:", outfile)
    
    for i in range(min_size, (max_size + 1)):
        for base1 in ['A', 'U', 'G', 'C']:
            key = base1 + str(i)
            if key in abun_count:
                # sample,countSize,type,firstBase,count
                iouthandle.write("{0},{1},abun,{2},{3}\n".format(sample_clean,
                                                           i, base1,
                                                           abun_count[key]))
                iouthandle.write("{0},{1},unique,{2},{3}\n".format(sample_clean,
                                                           i, base1,
                                                           uniq_count[key]))
            else:
                iouthandle.write("{0},{1},abun,{2},0\n".format(sample_clean,
                                                           i, base1))
                iouthandle.write("{0},{1},unique,{2},0\n".format(sample_clean,
                                                           i, base1))
    iouthandle.close
    return outfile
