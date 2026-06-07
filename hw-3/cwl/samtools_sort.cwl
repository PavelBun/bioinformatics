cwlVersion: v1.0
class: CommandLineTool
requirements:
  DockerRequirement:
    dockerPull: quay.io/biocontainers/samtools:1.9--h10a08f8_12
baseCommand: [samtools, sort]
arguments:
  - prefix: -o
    valueFrom: sample.sorted.bam
inputs:
  bam:
    type: File
    inputBinding:
      position: 1
outputs:
  sorted_bam:
    type: File
    outputBinding:
      glob: sample.sorted.bam
