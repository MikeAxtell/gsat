import os.path
import sys
import re
import multiprocessing
from Bio.SeqIO.FastaIO import SimpleFastaParser
import Levenshtein

def mature_search (alist):
    
    # Unpack the incoming tuple
    count_file = alist[0]
    queryFa = alist[1]
    odir = alist[2]
    maxEdit = alist[3]

    print(multiprocessing.current_process().name, "is working on", count_file)

    # get a dictionary of the queries, in upper-case U form
    qdict = get_qdict(queryFa)
    
    # determine output .csv file. This will be placed in the directory
    # specified on command line
    simple_name = get_simple_name(count_file)
    left_clean = re.sub('^.*\/', '', queryFa)
    outfile_mat = (odir.rstrip("/") + '/' +
                   simple_name + '.' + left_clean + '.gsat.mature.csv')

    if (os.path.isfile(outfile_mat)):
        return outfile_mat
    outhandle_mat = open(outfile_mat, "wt")
    #header = ("library," + 
              #"name,sequence,editDistance,raw,rpm,rpm_20-24\n")
              
    #outhandle_mat.write(header)

    all_reads = 0
    #dcl_reads = 0
    big_reads = {}
        
    with open(count_file, "rt") as count_handle:
        for count_line in count_handle:
            count_line = count_line.strip()
            count_fields = count_line.split(',')
            all_reads += int(count_fields[1])
            #if (len(count_fields[0]) > 19) and (len(count_fields[0]) < 25):
                #dcl_reads += int(count_fields[1])
            big_reads[count_fields[0]] = int(count_fields[1])

    for qseq in qdict:
        if qseq in big_reads:
            rpm = round(1E6 * (big_reads[qseq] / all_reads), 2)
            #rpmdcl = round(1E6 * (big_reads[qseq] / dcl_reads), 2)
            towrite = (simple_name + "," +
                        qdict[qseq] + "," + qseq + "," +
                        str("0") + "," + str(big_reads[qseq]) + "," +
                        str(rpm) + "\n")
                        #str(rpm) + "," + str(rpmdcl) + "\n")
        else:
            towrite = (simple_name + "," +
                        qdict[qseq] + "," + qseq + ',' +
                        str("0") + "," + str("0") + "," +
                        str("0.00") + "\n")
                        #str("0.00") + "," + str("0.00") + "\n")
                
        outhandle_mat.write(towrite)
        # Search for close variants using Levenshtein edit distance
        if maxEdit > 0:
            for rseq in big_reads:
                d = Levenshtein.distance(qseq, rseq)
                if(d > 0 and d <= maxEdit):
                    rpm = round(1E6 * (big_reads[rseq] / all_reads), 2)
                    #rpmdcl = round(1E6 * (big_reads[rseq] / dcl_reads), 2)
                    towrite = (simple_name + "," +
                        qdict[qseq] + "," + rseq + "," +
                        str(d) + "," + str(big_reads[rseq]) + "," +
                        str(rpm) + "\n")
                        #str(rpm) + "," + str(rpmdcl) + "\n")
                    outhandle_mat.write(towrite)

    outhandle_mat.close()
    return outfile_mat

def get_qdict (queryFa):
    queries = {}
    with open(queryFa) as fa_handle:
        for title, seq in SimpleFastaParser(fa_handle):
            seq = seq.upper()
            seq = seq.replace('T', 'U')
            if seq in queries:
                print("WARNING: query sequence", seq,
                      "was found more than once. Only one name will be kept.")
            else:
                # clean title at first white space -- no long FASTA headers!
                stitle = re.sub('\s.*$', '', title)
                queries[seq] = stitle
    return queries

def get_simple_name (count_file):
    # just strip off leading path and trailing .fastq or .fq from file name
    right_clean = re.sub('\.fq.*$|\.fastq.*$', '', count_file)
    clean = re.sub('^.*\/', '', right_clean)
    return clean


    
