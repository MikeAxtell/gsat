import argparse
import glob
import sys
import os.path
import re
from Bio.SeqIO.FastaIO import SimpleFastaParser


# versioning
version = '0.1'

# arguments and help message
parser=argparse.ArgumentParser(
    description="gsat: General SmallRNA-seq Analysis Tool " +
    'version: ' + version)
parser.add_argument('--directory',
                    help='REQUIRED path to directory containing sRNA-seq' +
                    ' fastq files (gz compressed is OK)',
                    required=True)
parser.add_argument('--metadata',
                    help='REQUIRED .csv file of metadata.' +
                    ' First column must be called \'sample\','+
                    ' additional columns are'+
                    ' factors.' +
                    ' Sample names must match sRNA-seq file names, ' +
                    ' stripped of .fastq.gz suffices.',
                    required=True)
parser.add_argument('--prefixSeq',
                    help='Sequence to use as a prefix key to search' +
                    ' for adapter.' +
                    ' Defaults to AAGCTCAGGAGGGATAGCGCC (ath-miR390a).' +
                    ' Should be DNA, upper-case',
                    default="AAGCTCAGGAGGGATAGCGCC")
parser.add_argument('--matureFa',
                    help='FASTA file of mature sRNA query(ies).' +
                    ' Can be DNA or RNA, upper or lower-case.' +
                    ' Must be all ATGUCatguc characters')
parser.add_argument("--noTrim", help="Don't trim - reads already trimmed",
                    action="store_true")
parser.add_argument('--adapterSeq',
                    help='Adapter sequence to use for trimming.' +
                    ' Applied to ALL libraries.' +
                    ' Should be DNA, upper-case.' +
                    ' If not specified, will be determined empirically')
parser.add_argument('--processors',
                    help='Number of processor cores to use for' +
                    ' fastq file processing.' +
                    ' Defaults to 1. Use more, depending on your machine,' +
                    ' in order to speed the analysis', type=int,
                    default=1)
parser.add_argument('--maxEdit',
                    help='Maximum edit distance for variant finding.' +
                    ' Set to 0 to drastically increase speed (but miss ' +
                    'all variants!)' +
                    ' Defaults to 2.', type=int, default=2)


args = parser.parse_args()

# files
fq_files = (glob.glob(args.directory.rstrip("/") + '/*.fq.gz') +
            glob.glob(args.directory.rstrip("/") + '/*.fastq.gz') +
            glob.glob(args.directory.rstrip("/") + '/*.fq') +
            glob.glob(args.directory.rstrip("/") + '/*.fastq'))

count_files = (glob.glob(args.directory.rstrip("/") + '/*.counts.csv'))


n_fq_files = len(fq_files)
n_c_files = len(count_files)

if n_c_files > 0:
    print("Found", n_c_files, "processed counts files to use.")
    extract = 0
elif n_fq_files < 1:
    print("No valid fastq files or counts files found!")
    sys.exit()
else:
    print("Found", n_fq_files, "valid fastq files to process.")
    extract = 1

# Validate existence of matureFa file, if user provided it
look = 0

if args.matureFa:
    if not (os.path.isfile(args.matureFa)):
        print("matureFa file was not found!")
        sys.exit()
    # metadata is required in this case
    if not args.metadata:
        print("A metadata csv file is required for this run!")
        sys.exit()

    # check if the .gsat.mature.csv file already exists, and adjust.
    left_clean = re.sub('^.*\/', '', args.matureFa)
    outfile_mat = (args.directory.rstrip("/") +
                   '/' + left_clean +
                   '.gsat.mature.csv')
    if os.path.isfile(outfile_mat):
        look = 0
    else:
        look = 1
else:
    # A dummy name, signifying nothing. Needed as a variable later.
    outfile_mat = (args.directory.rstrip("/") +
                '/' + 'empty' +
                '.gsat.mature.csv')


# Validate existence and contents of metadata file, which is required
if (args.metadata):
    if not (os.path.isfile(args.metadata)):
        print("metadata file was not found!")
        sys.exit()
    ### NO, need to allow a non matureFa run! 
    #if not args.matureFa:
        #print("using --metadata also requires --matureFa")
        #sys.exit()
    # Match metadata with the resident files
    # First store names from metadata
    md_handle = open(args.metadata)
    md_names = {}
    md_header = md_handle.readline()
    md_header = md_header.strip()

    # Some .csv files (I'm looking at you Excel) have BOMs
    # Instead of trying to guess the encoding, strip BOM if it's present
    md_header = re.sub('^\ufeff', '', md_header)
    md_header_fields = md_header.split(',')
    md_factors = {}
    for idx,factor in enumerate(md_header_fields):
        #print("idx:", idx, "factor:", factor)
        if not idx == 0:
            md_factors[idx] = factor
            if factor == 'sample':
                print("Invalid metadata file." +
                      " A factor cannot be named 'sample'.")
                sys.exit()
        else:
            if not factor == 'sample':
                print("Invalid metadata file." +
                      " The first column must be named 'sample'.")
                sys.exit()
    
    for md_line in md_handle:
        md_line = md_line.strip()
        md_fields = md_line.split(',')
        #md_left_clean = re.sub('^.*\/', '', md_fields[0])
        #md_clean = re.sub('\.fq.*$|\.fastq.*$', '', md_left_clean)
        md_names[md_fields[0]] = 1
    md_handle.close()

    
    # Scan through files, either fastq or count files, depending
    if (extract == 1):
        # Part 1: Every fq_file must have a match in the metadata
        for fq_file in fq_files:
            # remove leading path
            left_clean = re.sub('^.*\/', '', fq_file)
            clean = re.sub('\.fq.*$|\.fastq.*$', '', left_clean)
            if not (clean in md_names):
                print("name", clean, "not found in metadata!")
                sys.exit()
        # Part 2: number of md_names must equal number of fastq files
        if not (len(md_names) == len(fq_files)):
            sys.exit("metadata information does not match fastq files!")
    else:
        # then it's count files we are comparing to the metadata
        for count_file in count_files:
            # remove leading path
            left_clean = re.sub('^.*\/', '', count_file)
            clean = re.sub('\.fq.*$|\.fastq.*$', '', left_clean)
            if not (clean in md_names):
                print("name", clean, "not found in metadata!")
                sys.exit()
        # Part 2: number of md_names must equal number of count files
        if not (len(md_names) == len(count_files)):
            print("metadata information does not match count files!")
            sys.exit()


    
        
            


    
