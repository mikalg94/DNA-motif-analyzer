from io import StringIO

from Bio import Entrez
from Bio import SeqIO

from src.validation_utils import validate_dna_sequence


def fetch_sequence_from_ncbi(accession_id, email):
    if not accession_id:
        raise ValueError("Accession ID cannot be empty.")

    if not email:
        raise ValueError("Email is required for NCBI access.")

    Entrez.email = email

    try:
        handle = Entrez.efetch(
            db="nucleotide",
            id=accession_id,
            rettype="fasta",
            retmode="text"
        )

        fasta_data = handle.read()
        handle.close()

        if not fasta_data.strip():
            raise ValueError("No sequence data returned from NCBI.")

        record = SeqIO.read(StringIO(fasta_data), "fasta")
        sequence = str(record.seq).upper()

        validate_dna_sequence(sequence)
        return sequence

    except Exception as e:
        raise RuntimeError(f"NCBI download failed: {e}")