#!/bin/bash
set -e

mkdir -p data
cd data

echo "=== Скачивание референсного генома E. coli K-12 MG1655 ==="
if [ ! -f "reference.fna" ]; then
    echo "Скачивание reference.fna.gz..."
    curl -L -o reference.fna.gz "https://ftp.ncbi.nlm.nih.gov/genomes/all/GCF/000/005/845/GCF_000005845.2_ASM584v2/GCF_000005845.2_ASM584v2_genomic.fna.gz"
    echo "Распаковка reference.fna.gz..."
    gzip -d reference.fna.gz
    mv GCF_000005845.2_ASM584v2_genomic.fna reference.fna 2>/dev/null || true
else
    echo "Референсный геном уже скачан и распакован (reference.fna)."
fi

echo "=== Скачивание парно-концевых чтений DRR063440 (Illumina) ==="
if [ ! -f "DRR063440_1.fastq.gz" ]; then
    echo "Скачивание DRR063440_1.fastq.gz..."
    curl -L -o DRR063440_1.fastq.gz "https://ftp.sra.ebi.ac.uk/vol1/fastq/DRR063/DRR063440/DRR063440_1.fastq.gz"
else
    echo "Файл DRR063440_1.fastq.gz уже существует."
fi

if [ ! -f "DRR063440_2.fastq.gz" ]; then
    echo "Скачивание DRR063440_2.fastq.gz..."
    curl -L -o DRR063440_2.fastq.gz "https://ftp.sra.ebi.ac.uk/vol1/fastq/DRR063/DRR063440/DRR063440_2.fastq.gz"
else
    echo "Файл DRR063440_2.fastq.gz уже существует."
fi

echo "=== Скачивание завершено! ==="
ls -lh
