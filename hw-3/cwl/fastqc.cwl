cwlVersion: v1.0
class: CommandLineTool
requirements:
  DockerRequirement:
    dockerPull: biocontainers/fastqc:v0.11.9_cv8
  InitialWorkDirRequirement:
    listing: $(inputs.reads)
baseCommand: fastqc
arguments:
  - prefix: -o
    valueFrom: $(runtime.outdir)
inputs:
  reads:
    type: File[]
    inputBinding:
      position: 1
outputs:
  html_reports:
    type: File[]
    outputBinding:
      glob: "*.html"
  zip_reports:
    type: File[]
    outputBinding:
      glob: "*.zip"
