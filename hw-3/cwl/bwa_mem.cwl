cwlVersion: v1.0
class: CommandLineTool
requirements:
  DockerRequirement:
    dockerPull: biocontainers/bwa:v0.7.17_cv1
  InitialWorkDirRequirement:
    listing:
      - entry: $(inputs.reference)
baseCommand: [bwa, mem]
inputs:
  reference:
    type: File
    inputBinding:
      position: 1
      valueFrom: $(self.basename)
    secondaryFiles:
      - .amb
      - .ann
      - .bwt
      - .pac
      - .sa
  fastq1:
    type: File
    inputBinding:
      position: 2
  fastq2:
    type: File
    inputBinding:
      position: 3
outputs:
  sam:
    type: stdout
stdout: sample.sam
