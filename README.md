# gsat - General Small RNA-seq Analysis Tool

## Synopsis
Adapter trimming, quality control, and simple analyses of small RNA-seq data. Independent of alignments to a reference.

## Author
Michael J. Axtell, The Pennsylvania State University
University Park, PA 16802 USA
mja18@psu.edu

## Dependencies
* python3
* R , with libraries:
  * shiny
  * DT
  * DBI
  * ggplot2

## Install

??

## Usage
```
gsat [-h] --directory DIRECTORY --metadata METADATA
               [--prefixSeq PREFIXSEQ] [--matureFa MATUREFA] [--noTrim]
               [--adapterSeq ADAPTERSEQ] [--processors PROCESSORS]
               [--maxEdit MAXEDIT]
```

## Options
```
-h, --help            show this help message and exit
  --directory DIRECTORY
                        REQUIRED path to directory containing sRNA-seq fastq
                        files (gz compressed is OK)
  --metadata METADATA   REQUIRED .csv file of metadata. First column must be
                        called 'sample', additional columns are factors.
                        Sample names must match sRNA-seq file names, stripped
                        of .fastq.gz suffices.
  --prefixSeq PREFIXSEQ
                        Sequence to use as a prefix key to search for adapter.
                        Defaults to AAGCTCAGGAGGGATAGCGCC (ath-miR390a).
                        Should be DNA, upper-case
  --matureFa MATUREFA   FASTA file of mature sRNA query(ies). Can be DNA or
                        RNA, upper or lower-case. Must be all ATGUCatguc
                        characters
  --noTrim              Don't trim - reads already trimmed
  --adapterSeq ADAPTERSEQ
                        Adapter sequence to use for trimming. Applied to ALL
                        libraries. Should be DNA, upper-case. If not
                        specified, will be determined empirically
  --processors PROCESSORS
                        Number of processor cores to use for fastq file
                        processing. Defaults to 1. Use more, depending on your
                        machine, in order to speed the analysis
  --maxEdit MAXEDIT     Maximum edit distance for variant finding. Set to 0 to
                        drastically increase speed (but miss all variants!)
                        Defaults to 2.

```

## Important assumptions
If the assumptions below aren't met, you CAN'T use gsat with untrimmed .fastq reads!
* Untrimmed .fastq data are assumed to be single-end, + stranded reads from a standard small RNA-seq library. This means that the first base of each read corresponds to the first RNA nucleotide in the original small RNA.
* It is also assumed that each untrimmed read is longer than the original small RNA, such that, somewhere in the read, the adapter used in sequencing is part of the read. 

## Workflow
### Arrangement of inputs
A set of .fastq files is placed into a directory. These can be gzip compressed (file name must end in .gz), or not. In addition, a .csv file of metadata must also be prepared. This metadata file must have 'sample' as the header for the first column, and then one or more factors in subequent columns. Samples are specified by their 'base name' .. which is the .fastq file name with the .fastq (and anything after the .fastq eg. `/.fastq.*$/` removed.

Optionally, a file of one or more small RNA queries in FASTA format can also be prepared.

### Identification of the 3'-adapter sequence
For each .fastq file, the 3'-adapter sequence is empirically determined. To do this, all of the reads are scanned to find those that begin with a known microRNA sequence, provided by option `--prefixSeq`. By default, this is set to `AAGCTCAGGAGGGATAGCGCC`, which is miR390. miR390 is deeply conserved among land plants, but won't be suitable for other species, so adjust `--prefixSeq` according to your specific situation.

Once scanned, the most common 3' suffix is kept. If the suffix is longer than 20 bases, it is trimmed back to the first 20 bases.

If you already know the 3' adapter sequences for the libraries in your experiment **and** it is the same for **all** libraries, you can bybass this search by providing the adapter sequence with option `--adapterSeq`.

### Trimming of 3'-adapter sequence
Once the first 20 bases of the 3'-adapter are inferred, the reads trimmed based on finding an exact match to those 20 bases. Thus, the longest possible trimmed read is the read length - 20. For each read, there are four possible outcomes:
* No adapter found. This will include sequencing errors, and RNAs that were too long to have the adapter present.
* No insert found. These are cases where the adapter itself is the first thing sequenced. These can be common and probably derived from PCR artifacts during library construction.
* Too short. Reads that are 1-5 nucleotides after trimming are not retained.
* Output. These are properly trimmed reads 6 nucleotides or longer that are output

Adapter trimming can be skipped using the switch `--noTrim`.

### Summarizing libraries
The lengths and 5'-nucleotides of all successfully trimmed sRNAs are summarized. The data are computed both in terms of "abundance" and "uniques". The "abundance" metric counts all reads, while the "unique" metric counts each unique sequence only once.

### Queries
Optionally, one or more small RNAs of interest can be analyzed by providing them as a FASTA file to option `--matureFa`. These sequences can be provided in DNA or RNA form (T or U) and upper- or lower-case. Each queried sequence is searched and tabulated, and reported.

#### Variants
By default, the query analysis will also report any variants up to a [Levenshtein distance](https://en.wikipedia.org/wiki/Levenshtein_distance) of 2. This is because such variants are often quite numerous for microRNAs and other types of sRNAs. The edit distance allowed can be changed with option `--maxEdit`. Setting `--maxEdit` to 0 will speed up the search considerably, but won't return any close variants.

## Outputs
### Flat files

* for each fastq file, there will be a corresponding fastq.trimmed file, showing the adapter trimmed data in fastq format
* for each fastq.trimmed file, there will be a corresponding .counts.csv file, which shows each unique sRNA sequence, and the number of reads. The order of the sequence is arbitrary.
* a triminfo.csv file, that summarizes the results of adapter trimming
* a libinfo.csv file, that summarizes sRNA lengths and 5'-nucleotides from the successfully trimmed sRNAs

### Other files

* a gsat.app.R file, which is an R-script that, when run, allows interactive analysis of the results. When executed, copy and paste the given url to a web browser. This R script requires the following libraries be available to R:
    * shiny
    * DT
    * DBI
    * ggplot2
* a .gsat.sqlite file. This is an sqlite database, intended primarily for the R script's use. But it can also be queried using any valid sqlite interface/protocol.

## Performance
* Use the option `--processors` to increase the processor cores. Do not use a value for `--processors` that exceeds the number of input .fastq files.
* If analyzing queries using option `--matureFa`, setting the option `--maxEdit` to 0 will speed up the analysis (but will not allow recovery of any close variants to the query sequences).

## Testing

??

 

