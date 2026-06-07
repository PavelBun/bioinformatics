cwlVersion: v1.0
class: CommandLineTool
requirements:
  DockerRequirement:
    dockerPull: quay.io/biocontainers/samtools:1.9--h10a08f8_12
  InitialWorkDirRequirement:
    listing:
      - entry: $(inputs.bam)
        writable: true
baseCommand: [samtools, index]
inputs:
  bam:
    type: File
    inputBinding:
      position: 1
outputs:
  indexed_bam:
    type: File
    outputBinding:
      glob: $(inputs.bam.basename)
    secondaryFiles:
      - .bai
