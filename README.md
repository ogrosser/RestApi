# RestApi
This project demonstrates using RESTApi with mygene and Ensembl to obtain homologs to a chosen gene. Mygene is used for the Ensembl ID, and Ensembl is used to get the nucleotide sequence and homologs.

The script api.py can be executed by typing the following into your terminal:
    python3 api.py
NOTE: Make sure there are no existing output files in your directory before executing.

When executed, api.py will ask you to input a valid gene that exists in humans. If the gene is not valid, you will be prompted to try again.

The outputs for this project are:
1. {gene}.fasta - contains the genomic sequence of the user inputted gene and the translation of the longest open reading frame
2. {gene}_homology_list.txt -> contains a list of all the species that have genes that are homologous to the user inputted gene
