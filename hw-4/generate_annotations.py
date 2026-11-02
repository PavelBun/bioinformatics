"""
Скрипт полной клинической аннотации генетических вариантов для задания 4.
Вариант 16 (student_16.vcf).
Сборка: GRCh38.
Источники: Ensembl VEP (v116 / REST API), ClinVar (NCBI), gnomAD (v4 / v3 via VEP).
"""

import os
import json
import pandas as pd

def analyze_vcf_stats(vcf_path):
    with open(vcf_path, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip()]

    header = [l for l in lines if l.startswith('#')]
    records = [l.split('\t') for l in lines if not l.startswith('#')]

    ti_pairs = {('A', 'G'), ('G', 'A'), ('C', 'T'), ('T', 'C')}
    chr_counts = {}
    transitions = 0
    transversions = 0

    for r in records:
        chrom, pos, id_, ref, alt = r[0], r[1], r[2], r[3], r[4]
        chr_counts[chrom] = chr_counts.get(chrom, 0) + 1
        if (ref, alt) in ti_pairs:
            transitions += 1
        else:
            transversions += 1

    stats = {
        'total_variants': len(records),
        'chr_counts': chr_counts,
        'transitions': transitions,
        'transversions': transversions,
        'ti_tv_ratio': round(transitions / transversions, 2) if transversions > 0 else 0
    }
    return stats, records

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    vcf_path = os.path.join(base_dir, 'student_16.vcf')
    stats, records = analyze_vcf_stats(vcf_path)
    print("VCF Statistics:")
    print(f"  Total records: {stats['total_variants']}")
    print(f"  Chromosomes: {stats['chr_counts']}")
    print(f"  Transitions (Ti): {stats['transitions']}")
    print(f"  Transversions (Tv): {stats['transversions']}")
    print(f"  Ti/Tv ratio: {stats['ti_tv_ratio']}")

    # Загружаем предзагруженные полные результаты VEP REST API
    raw_json_path = os.path.join(base_dir, 'vep_raw_results.json')
    with open(raw_json_path, 'r', encoding='utf-8') as f:
        vep_data = json.load(f)

    # 1. Построение сводной таблицы на 50 строк по требованиям задания
    summary_rows = []
    vep_export_rows = []
    clinvar_export_rows = []
    gnomad_export_rows = []

    # Словарь перевода последствий на русский для наглядности в отчете
    consequence_ru = {
        'synonymous_variant': 'синонимичный вариант (synonymous)',
        'missense_variant': 'миссенс-вариант (missense)',
        'stop_gained': 'нонсенс-мутация / появление стоп-кодона (stop gained)',
        'frameshift_variant': 'сдвиг рамки считывания (frameshift)',
        'splice_donor_variant': 'донорный сайт сплайсинга',
        'splice_acceptor_variant': 'акцепторный сайт сплайсинга',
        'splice_region_variant': 'область сайта сплайсинга',
        '5_prime_UTR_variant': '5-UTR вариант',
        '3_prime_UTR_variant': '3-UTR вариант',
        'intron_variant': 'интронный вариант',
        'upstream_gene_variant': 'апстрим регуляторная область',
        'downstream_gene_variant': 'даунстрим регуляторная область',
        'intergenic_variant': 'межгенный вариант'
    }

    clinvar_interp_ru = {
        'benign': 'Доброкачественный (Benign)',
        'likely_benign': 'Вероятно доброкачественный (Likely Benign)',
        'uncertain_significance': 'Неопределенного значения (VUS)',
        'pathogenic': 'Патогенный (Pathogenic)',
        'likely_pathogenic': 'Вероятно патогенный (Likely Pathogenic)',
        'conflicting_classifications': 'Противоречивая интерпретация (Conflicting classifications)'
    }

    for idx, (rec, v) in enumerate(zip(records, vep_data)):
        chrom, pos, orig_id, ref, alt = rec[0], rec[1], rec[2], rec[3], rec[4]
        coord_id = f"chr{chrom}:{pos}_{ref}>{alt}"
        
        # Анализ транскриптов и выбор наиболее значимого транскрипта
        transcripts = v.get('transcript_consequences', [])
        
        # Иерархия выбора транскрипта:
        # 1. MANE Select (консенсусный транскрипт NCBI & EMBL-EBI для клинической генетики)
        # 2. Ensembl Canonical (основной транскрипт Ensembl)
        # 3. Наиболее тяжелое последствие (Most Severe) среди всех транскриптов
        selected_tx = None
        rule_description = ""

        # Проверяем MANE Select
        mane_candidates = [t for t in transcripts if t.get('mane_select')]
        if mane_candidates:
            selected_tx = mane_candidates[0]
            rule_description = f"MANE Select ({selected_tx.get('mane_select')})"
        else:
            canonical_candidates = [t for t in transcripts if t.get('canonical') == 1]
            if canonical_candidates:
                selected_tx = canonical_candidates[0]
                rule_description = f"Ensembl Canonical ({selected_tx.get('transcript_id')})"
            elif transcripts:
                selected_tx = transcripts[0]
                rule_description = f"Ensembl First / Most severe ({selected_tx.get('transcript_id')})"
            else:
                selected_tx = None
                rule_description = "Межгенный регион (нет транскриптов)"

        if selected_tx:
            gene_symbol = selected_tx.get('gene_symbol', selected_tx.get('gene_id', 'N/A'))
            conseq_terms = selected_tx.get('consequence_terms', [])
            conseq_str = ", ".join(conseq_terms)
            hgvsc = selected_tx.get('hgvsc', '')
            hgvsp = selected_tx.get('hgvsp', '')
            protein_change = selected_tx.get('amino_acids', '')
            codons = selected_tx.get('codons', '')
            sift = selected_tx.get('sift_prediction', '')
            sift_score = selected_tx.get('sift_score', '')
            polyphen = selected_tx.get('polyphen_prediction', '')
            polyphen_score = selected_tx.get('polyphen_score', '')
            biotype = selected_tx.get('biotype', '')
            tx_id = selected_tx.get('transcript_id', '')
        else:
            gene_symbol = "Intergenic"
            conseq_str = v.get('most_severe_consequence', 'intergenic_variant')
            hgvsc = ""
            hgvsp = ""
            protein_change = ""
            codons = ""
            sift = ""
            sift_score = ""
            polyphen = ""
            polyphen_score = ""
            biotype = "intergenic"
            tx_id = ""

        # Идентификатор rsID
        rsid = orig_id if orig_id.startswith('rs') else None
        colocs = v.get('colocated_variants', [])
        for c in colocs:
            cid = c.get('id', '')
            if cid.startswith('rs'):
                rsid = cid

        # Частоты gnomAD
        gnomad_exome_af = None
        gnomad_genome_af = None
        gnomad_pop_freqs = {}

        for c in colocs:
            freqs = c.get('frequencies', {})
            allele_freqs = freqs.get(alt, {})
            if not allele_freqs and freqs:
                allele_freqs = list(freqs.values())[0]
            
            if allele_freqs:
                if 'gnomade' in allele_freqs:
                    gnomad_exome_af = allele_freqs['gnomade']
                if 'gnomadg' in allele_freqs:
                    gnomad_genome_af = allele_freqs['gnomadg']
                for k, val in allele_freqs.items():
                    if k.startswith('gnomad') or k in ['af', 'afr', 'eur', 'eas', 'sas', 'amr']:
                        gnomad_pop_freqs[k] = val

        gnomad_parts = []
        if gnomad_genome_af is not None:
            gnomad_parts.append(f"gnomAD Genomes AF: {gnomad_genome_af:.6f}")
        if gnomad_exome_af is not None:
            gnomad_parts.append(f"gnomAD Exomes AF: {gnomad_exome_af:.6f}")
        
        if gnomad_parts:
            gnomad_af_display = " | ".join(gnomad_parts)
        else:
            gnomad_af_display = "Не обнаружен в gnomAD"

        # ClinVar аннотация
        clin_sigs = []
        clinvar_ids = []
        for c in colocs:
            if c.get('clin_sig'):
                clin_sigs.extend(c.get('clin_sig'))
            cid = c.get('id', '')
            if cid.startswith('RCV') or cid.startswith('VCV'):
                clinvar_ids.append(cid)

        # Удаляем дубликаты
        clin_sigs = list(dict.fromkeys(clin_sigs))
        
        if clin_sigs:
            clinvar_present = "Есть"
            clinvar_interp_raw = ", ".join(clin_sigs)
            # Человекочитаемая интерпретация
            clinvar_interp_human = ", ".join([clinvar_interp_ru.get(cs.lower(), cs) for cs in clin_sigs])
        else:
            clinvar_present = "Нет записи"
            clinvar_interp_raw = "Not reported"
            clinvar_interp_human = "Отсутствует в ClinVar"

        # Формируем строку основной сводной таблицы (50 вариантов)
        summary_rows.append({
            '№': idx + 1,
            'Координаты (REF>ALT)': coord_id,
            'rsID': rsid if rsid else 'N/A',
            'Ген': gene_symbol,
            'Наиболее значимое последствие по VEP': conseq_str,
            'Правило выбора транскрипта': rule_description,
            'gnomAD Allele Frequency': gnomad_af_display,
            'Запись ClinVar': clinvar_present,
            'Клиническая интерпретация ClinVar': clinvar_interp_human,
            # Дополнительные полезные столбцы для полноты
            'Транскрипт': tx_id,
            'HGVSc': hgvsc,
            'HGVSp': hgvsp,
            'SIFT': f"{sift} ({sift_score})" if sift else "-",
            'PolyPhen': f"{polyphen} ({polyphen_score})" if polyphen else "-"
        })

        # Формируем строки для экспорта gnomAD
        gnomad_export_rows.append({
            '№': idx + 1,
            'Variant_ID': coord_id,
            'rsID': rsid if rsid else 'N/A',
            'Gene': gene_symbol,
            'gnomAD_Genomes_AF': gnomad_genome_af if gnomad_genome_af is not None else 'N/A',
            'gnomAD_Exomes_AF': gnomad_exome_af if gnomad_exome_af is not None else 'N/A',
            'gnomAD_Genomes_AFR': gnomad_pop_freqs.get('gnomadg_afr', 'N/A'),
            'gnomAD_Genomes_EUR': gnomad_pop_freqs.get('gnomadg_nfe', 'N/A'),
            'gnomAD_Genomes_EAS': gnomad_pop_freqs.get('gnomadg_eas', 'N/A'),
            'gnomAD_Genomes_SAS': gnomad_pop_freqs.get('gnomadg_sas', 'N/A'),
            'gnomAD_Genomes_AMR': gnomad_pop_freqs.get('gnomadg_amr', 'N/A')
        })

        # Формируем строки для экспорта ClinVar
        clinvar_export_rows.append({
            '№': idx + 1,
            'Variant_ID': coord_id,
            'rsID': rsid if rsid else 'N/A',
            'Gene': gene_symbol,
            'ClinVar_Status': clinvar_present,
            'ClinVar_Significance_Raw': clinvar_interp_raw,
            'ClinVar_Significance_RU': clinvar_interp_human
        })

        # Формируем подробный экспорт всех последствий транскриптов по стандарту VEP
        for t in transcripts:
            vep_export_rows.append({
                'Uploaded_variation': orig_id,
                'Location': f"{chrom}:{pos}",
                'Allele': alt,
                'Gene': t.get('gene_symbol', t.get('gene_id', '-')),
                'Feature': t.get('transcript_id', '-'),
                'Feature_type': 'Transcript',
                'Consequence': ",".join(t.get('consequence_terms', [])),
                'cDNA_position': t.get('cdna_start', '-'),
                'CDS_position': t.get('cds_start', '-'),
                'Protein_position': t.get('protein_start', '-'),
                'Amino_acids': t.get('amino_acids', '-'),
                'Codons': t.get('codons', '-'),
                'Existing_variation': rsid if rsid else '-',
                'IMPACT': t.get('impact', '-'),
                'BIOTYPE': t.get('biotype', '-'),
                'CANONICAL': 'YES' if t.get('canonical') == 1 else 'NO',
                'MANE_SELECT': t.get('mane_select', '-'),
                'SIFT': f"{t.get('sift_prediction')}({t.get('sift_score')})" if t.get('sift_prediction') else '-',
                'PolyPhen': f"{t.get('polyphen_prediction')}({t.get('polyphen_score')})" if t.get('polyphen_prediction') else '-',
                'CLIN_SIG': clinvar_interp_raw,
                'gnomADg_AF': gnomad_genome_af if gnomad_genome_af is not None else '-',
                'gnomADe_AF': gnomad_exome_af if gnomad_exome_af is not None else '-'
            })

    # Сохраняем датафреймы
    df_summary = pd.DataFrame(summary_rows)
    df_vep = pd.DataFrame(vep_export_rows)
    df_clinvar = pd.DataFrame(clinvar_export_rows)
    df_gnomad = pd.DataFrame(gnomad_export_rows)

    # 1. Аннотированная сводная таблица (50 строк)
    df_summary.to_csv(os.path.join(base_dir, 'annotated_variants_50.tsv'), sep='\t', index=False, encoding='utf-8')
    df_summary.to_csv(os.path.join(base_dir, 'annotated_variants_50.csv'), index=False, encoding='utf-8-sig')
    df_summary.to_excel(os.path.join(base_dir, 'annotated_variants_50.xlsx'), index=False)
    print("Saved annotated_variants_50.tsv, .csv, .xlsx (50 rows)")

    # 2. Результат аннотации VEP (экспорт)
    df_vep.to_csv(os.path.join(base_dir, 'vep_annotation_export.txt'), sep='\t', index=False, encoding='utf-8')
    df_vep.to_csv(os.path.join(base_dir, 'vep_annotation_export.tsv'), sep='\t', index=False, encoding='utf-8')
    print(f"Saved vep_annotation_export.tsv ({len(df_vep)} transcript consequence rows)")

    # 3. Результат аннотации ClinVar (экспорт)
    df_clinvar.to_csv(os.path.join(base_dir, 'clinvar_annotation_export.tsv'), sep='\t', index=False, encoding='utf-8')
    df_clinvar.to_excel(os.path.join(base_dir, 'clinvar_annotation_export.xlsx'), index=False)
    print("Saved clinvar_annotation_export.tsv, .xlsx")

    # 4. Результат аннотации gnomAD (экспорт)
    df_gnomad.to_csv(os.path.join(base_dir, 'gnomad_annotation_export.tsv'), sep='\t', index=False, encoding='utf-8')
    df_gnomad.to_excel(os.path.join(base_dir, 'gnomad_annotation_export.xlsx'), index=False)
    print("Saved gnomad_annotation_export.tsv, .xlsx")

    # Сводные статистики
    print("\n--- Summary Statistics ---")
    print("Consequences distribution (on selected transcripts):")
    print(df_summary['Наиболее значимое последствие по VEP'].value_counts())
    print("\nClinVar status:")
    print(df_summary['Запись ClinVar'].value_counts())
    print("\nClinVar interpretations:")
    print(df_summary['Клиническая интерпретация ClinVar'].value_counts())

if __name__ == '__main__':
    main()
