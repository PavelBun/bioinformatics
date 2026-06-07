#!/bin/bash
set -e

export MSYS_NO_PATHCONV=1

echo "=== Запуск конвейера вызова генетических вариантов ==="

DATA_DIR="$(pwd)/data"

echo "=== Шаг 1: Контроль качества исходных чтений (FastQC) ==="
docker run --rm -v "${DATA_DIR}:/data" biocontainers/fastqc:v0.11.9_cv8 fastqc -o /data /data/DRR063440_1.fastq.gz /data/DRR063440_2.fastq.gz

echo "=== Шаг 2: Индексирование референсного генома (BWA index) ==="
docker run --rm -v "${DATA_DIR}:/data" biocontainers/bwa:v0.7.17_cv1 bwa index /data/reference.fna

echo "=== Шаг 2.5: Создание индекса референсного генома .fai (samtools faidx) ==="
docker run --rm -v "${DATA_DIR}:/data" quay.io/biocontainers/samtools:1.9--h10a08f8_12 samtools faidx /data/reference.fna

echo "=== Шаг 3: Картирование чтений на референсный геном (BWA mem) ==="
docker run --rm -v "${DATA_DIR}:/data" biocontainers/bwa:v0.7.17_cv1 bwa mem /data/reference.fna /data/DRR063440_1.fastq.gz /data/DRR063440_2.fastq.gz > data/sample.sam

echo "=== Шаг 4: Конвертация SAM в BAM (samtools view) ==="
docker run --rm -v "${DATA_DIR}:/data" quay.io/biocontainers/samtools:1.9--h10a08f8_12 samtools view -bS /data/sample.sam -o /data/sample.bam

echo "=== Шаг 5: Сбор статистики картирования (samtools flagstat) ==="
docker run --rm -v "${DATA_DIR}:/data" quay.io/biocontainers/samtools:1.9--h10a08f8_12 samtools flagstat /data/sample.bam > data/sample_flagstat.txt

echo "=== Шаг 6: Оценка качества картирования ==="
python parse_flagstat.py data/sample_flagstat.txt > data/assessment_result.txt || true
cat data/assessment_result.txt

if grep -Fxq "OK" data/assessment_result.txt; then
    echo "Процент картирования превышает 90%. Продолжаем работу..."
    
    echo "=== Шаг 7: Сортировка BAM-файла (samtools sort) ==="
    docker run --rm -v "${DATA_DIR}:/data" quay.io/biocontainers/samtools:1.9--h10a08f8_12 samtools sort /data/sample.bam -o /data/sample.sorted.bam
    
    echo "=== Шаг 7.5: Индексация BAM-файла (samtools index) ==="
    docker run --rm -v "${DATA_DIR}:/data" quay.io/biocontainers/samtools:1.9--h10a08f8_12 samtools index /data/sample.sorted.bam
    
    echo "=== Шаг 8: Вызов вариантов (freebayes) ==="
    docker run --rm -v "${DATA_DIR}:/data" quay.io/biocontainers/freebayes:1.3.10--hbefcdb2_0 freebayes -f /data/reference.fna /data/sample.sorted.bam > data/sample.vcf
    
    echo "Finished"
else
    echo "not OK: Процент картирования ниже или равен 90%. Работа конвейера остановлена."
    exit 3
fi
