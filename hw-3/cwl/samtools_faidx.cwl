cwlVersion: v1.0
class: CommandLineTool
requirements:
  DockerRequirement:
    dockerPull: quay.io/biocontainers/samtools:1.9--h10a08f8_12
  InitialWorkDirRequirement:
    listing:
      - entry: $(inputs.reference)
        writable: true
baseCommand: [samtools, faidx]
inputs:
  reference:
    type: File
    inputBinding:
      position: 1
      valueFrom: $(self.basename)
outputs:
  indexed_reference:
    type: File
    outputBinding:
      glob: $(inputs.reference.basename)
    secondaryFiles:
      - .fai
      - .amb?
      - .ann?
      - .bwt?
      - .pac?
      - .sa?
