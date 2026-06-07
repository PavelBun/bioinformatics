cwlVersion: v1.0
class: CommandLineTool
requirements:
  DockerRequirement:
    dockerPull: quay.io/biocontainers/freebayes:1.3.10--hbefcdb2_0
  InitialWorkDirRequirement:
    listing:
      - entry: $(inputs.reference)
      - entry: $(inputs.bam)
baseCommand: freebayes
arguments:
  - prefix: -f
    valueFrom: $(inputs.reference.basename)
    position: 1
inputs:
  reference:
    type: File
    secondaryFiles:
      - .fai
  bam:
    type: File
    inputBinding:
      position: 2
      valueFrom: $(self.basename)
    secondaryFiles:
      - .bai
outputs:
  vcf:
    type: stdout
stdout: sample.vcf
