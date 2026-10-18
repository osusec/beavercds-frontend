apiVersion: v1
kind: ConfigMap

metadata:
  name: {{ include "beavercds-frontend.fullname" . }}-django-settings
  labels:
    {{- include "beavercds-frontend.labels" . | nindent 4 }}
  annotations:
    "helm.sh/hook": pre-install,pre-upgrade
    "helm.sh/hook-weight": "0"

data:
  helm_settings.py: |
    {{- .Values.config | nindent 4 }}
