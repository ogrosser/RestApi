#Goal: Use REST Api for mygene and ensembl databases to get the genomic sequence of your chosen gene. Said gene should exist
#in homo sapiens. Use biopython to translate the longest open reading frame. Then use ensembl to make a list of all the species
#that have homologous genes to said chosen gene.
#Author: Ondine Grosser

import requests #Allows for interaction with REST Api
import re #Allows for use of regular expression
from Bio.Seq import Seq #Allows for use of Seq class from BioPython
import os #Allows interaction with OS
import sys #Allows interaction with Python interpreter

gene = input("PLease enter valid gene that exists in the human species (examples: BRCA1, brca1, CDK2, cdk2): ") #Asks user to input gene
server = 'https://mygene.info/v3' #mygene database REST Api server
endpoint = '/query?q=' + gene + '&species=human' #Endpoint specifies input gene in human species as search parameters
r = requests.get(server + endpoint) #Searching mygene for input gene in human species

if r.status_code != 200: #If request did not go through
    print("Request failed. Run script again and enter valid gene.")
elif r.json()['total'] == 0: #If number of returned genes is zero
    print("Entered gene is either not valid or does not exist in the human species. Run script again and enter valid gene.")
else:
    r = r.json()
    gene_id = r['hits'][0]['_id'] #Gene ID
    endpoint2 = '/gene/' + gene_id #Endpoint specifies gene ID as search parameter
    r2 = requests.get(server + endpoint2) #Searching mygene for complete gene annotation
    r2 = r2.json()
    ensembl_id = r2['ensembl']['gene'] #Ensembl gene ID

    e_server = 'https://rest.ensembl.org' #Ensembl database REST Api server
    e_endpoint = '/sequence/id/' + ensembl_id + '?' + 'type=genomic' #Specifies search for genomic sequence
    e_req = requests.get(e_server + e_endpoint, headers = {"Content-Type" : "text/x-fasta"}) #Request will be returned as FASTA format
    if not e_req.ok: #If request did not go through, return HTTPError and exit server
        e_req.raise_for_status()
        sys.exit()
    o = open(gene + ".fasta", "a") #Creates FASTA file
    o.write(e_req.text) #Writes genomic sequence to FASTA file
    o.close()

    with open(gene + '.fasta', 'r') as s:
        seq = "".join(line.strip() for line in s) #Concatanate FASTA file contents to seq variable
    s.close()
    orf = max(re.findall(r'ATG(?:(?!TAA|TAG|TGA)...)*(?:TAA|TAG|TGA)', seq), key = len) #Finds longest open reading frame in seq variable
    amino = Seq(str(orf)).translate(table = 1) #Translates the open reading frame to an amino acid sequence
    with open(gene + '.fasta', 'a') as s:
        s.write('>' + gene + '_orf_translated\n' + str(amino) + '\n') #Add translated open reading frame to FASTA file.
    s.close()

    o = open("temp.txt", 'x') #Create temp text file
    o.close()

    with open('temp.txt', 'a') as h:
        #Specifies homologous genes of human input gene and condensed format as search parameters
        homo_endpoint = '/homology/id/human/' + ensembl_id + '?format=condensed'
        r3 = requests.get(e_server + homo_endpoint, headers={ "Content-Type" : "application/json"}) #Searches ensembl database
        if not r3.ok: #If request did not go through, return HTTPError and exit server
            r3.raise_for_status()
            sys.exit()
        r3 = r3.json()
        for i in r3['data'][0]['homologies']: #For each homologous gene:
            h.write(str(i['species']) + '\n') #Writes species to temp text file
    h.close()

    out_file = open(gene + "_homology_list.txt", "a") #Create homology list text file
    in_file = open("temp.txt", "r")
    existingLines = set()
    for line in in_file: #For every line in temp text file:
        if line not in existingLines: #Adds all lines except duplicate lines to homology list file
            out_file.write(line)
            existingLines.add(line)
    in_file.close()
    out_file.close()
    os.remove("temp.txt") #Removes temp file