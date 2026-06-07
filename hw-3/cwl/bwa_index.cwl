cwlVersion: v1.0
class: CommandLineTool
requirements:
  DockerRequirement:
    dockerPull: biocontainers/bwa:v0.7.17_cv1
  InitialWorkDirRequirement:
    listing:
      - entry: $(inputs.reference)
        writable: true
baseCommand: [bwa, index]
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
      - .amb
      - .ann
      - .bwt
      - .pac
      - .sa
