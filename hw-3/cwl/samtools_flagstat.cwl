cwlVersion: v1.0
class: CommandLineTool
requirements:
  DockerRequirement:
    dockerPull: quay.io/biocontainers/samtools:1.9--h10a08f8_12
baseCommand: [samtools, flagstat]
inputs:
  bam:
    type: File
    inputBinding:
      position: 1
outputs:
  flagstat_report:
    type: stdout
stdout: sample_flagstat.txt
