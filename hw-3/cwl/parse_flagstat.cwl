cwlVersion: v1.0
class: CommandLineTool
requirements:
  DockerRequirement:
    dockerPull: python:3.10-slim
baseCommand: python
inputs:
  script:
    type: File
    inputBinding:
      position: 1
  flagstat_report:
    type: File
    inputBinding:
      position: 2
outputs:
  assessment_result:
    type: stdout
stdout: assessment_result.txt
