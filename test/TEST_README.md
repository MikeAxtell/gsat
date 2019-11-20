# gsat testing and demonstration


## Get the test folder from github (come back to this)

## Retrieve some small RNA-seq data

We'll get data from SRA, using fasterq-dump from [sratools](https://www.ncbi.nlm.nih.gov/sra/docs/toolkitsoft/). These are untrimmed, 50nt reads.

`fasterq-dump SRR6074038`
`fasterq-dump SRR6074040`
`fasterq-dump SRR6074031`

## Run the test

This uses the provided metadata and query FASTA file

`python3 gsat.py --directory . --metadata gsat_TEST_metadata.csv --matureFa gsat_TEST_queries.fasta --processors 3`

We used three processor cores in the above .. with only three files to process there will be no gains to requesting more. 

## Examine the results

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








