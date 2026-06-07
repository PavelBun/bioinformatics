cwlVersion: v1.2
class: Workflow
requirements:
  InlineJavascriptRequirement: {}
  StepInputExpressionRequirement: {}
  MultipleInputFeatureRequirement: {}
  DockerRequirement: {}

inputs:
  fastq1:
    type: File
  fastq2:
    type: File
  reference:
    type: File
  parser_script:
    type: File

outputs:
  fastqc_html_reports:
    type: File[]
    outputSource: fastqc/html_reports
  fastqc_zip_reports:
    type: File[]
    outputSource: fastqc/zip_reports
  sam:
    type: File
    outputSource: bwa_mem/sam
  bam:
    type: File
    outputSource: samtools_view/bam
  flagstat_report:
    type: File
    outputSource: samtools_flagstat/flagstat_report
  assessment_result:
    type: File
    outputSource: parse_flagstat/assessment_result
  sorted_bam:
    type: File?
    outputSource: sort_bam/sorted_bam
  indexed_bam:
    type: File?
    outputSource: index_bam/indexed_bam
  vcf:
    type: File?
    outputSource: freebayes/vcf

steps:
  fastqc:
    run: fastqc.cwl
    in:
      reads:
        source: [fastq1, fastq2]
    out: [html_reports, zip_reports]

  bwa_index:
    run: bwa_index.cwl
    in:
      reference: reference
    out: [indexed_reference]

  samtools_faidx:
    run: samtools_faidx.cwl
    in:
      reference: bwa_index/indexed_reference
    out: [indexed_reference]

  bwa_mem:
    run: bwa_mem.cwl
    in:
      reference: samtools_faidx/indexed_reference
      fastq1: fastq1
      fastq2: fastq2
    out: [sam]

  samtools_view:
    run: samtools_view.cwl
    in:
      sam: bwa_mem/sam
    out: [bam]

  samtools_flagstat:
    run: samtools_flagstat.cwl
    in:
      bam: samtools_view/bam
    out: [flagstat_report]

  parse_flagstat:
    run: parse_flagstat.cwl
    in:
      script: parser_script
      flagstat_report: samtools_flagstat/flagstat_report
    out: [assessment_result]

  sort_bam:
    run: samtools_sort.cwl
    when: $(inputs.is_ok)
    in:
      is_ok:
        source: parse_flagstat/assessment_result
        loadContents: true
        valueFrom: $(self.contents.trim() === "OK")
      bam: samtools_view/bam
    out: [sorted_bam]

  index_bam:
    run: samtools_index.cwl
    when: $(inputs.is_ok)
    in:
      is_ok:
        source: parse_flagstat/assessment_result
        loadContents: true
        valueFrom: $(self.contents.trim() === "OK")
      bam: sort_bam/sorted_bam
    out: [indexed_bam]

  freebayes:
    run: freebayes.cwl
    when: $(inputs.is_ok)
    in:
      is_ok:
        source: parse_flagstat/assessment_result
        loadContents: true
        valueFrom: $(self.contents.trim() === "OK")
      reference: samtools_faidx/indexed_reference
      bam: index_bam/indexed_bam
    out: [vcf]
