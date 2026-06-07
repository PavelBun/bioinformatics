cwlVersion: v1.0
class: CommandLineTool
requirements:
  DockerRequirement:
    dockerPull: quay.io/biocontainers/samtools:1.9--h10a08f8_12
baseCommand: [samtools, view]
arguments:
  - -b
  - -S
  - prefix: -o
    valueFrom: sample.bam
inputs:
  sam:
    type: File
    inputBinding:
      position: 1
outputs:
  bam:
    type: File
    outputBinding:
      glob: sample.bam
