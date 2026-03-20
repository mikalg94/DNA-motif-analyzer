from Bio import Entrez
from Bio import SeqIO
from io import StringIO


def fetch_sequence_from_ncbi(accession_id, email):
    Entrez.email = email

    handle = Entrez.efetch(
        db="nucleotide",
        id=accession_id,
        rettype="fasta",
        retmode="text"
    )

    fasta_data = handle.read()
    handle.close()

    record = SeqIO.read(StringIO(fasta_data), "fasta")
    return str(record.seq)