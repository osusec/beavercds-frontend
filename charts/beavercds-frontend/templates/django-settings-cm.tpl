apiVersion: v1
kind: ConfigMap

metadata:
  name: {{ include "beavercds-frontend.fullname" . }}-django-settings
  labels:
    {{- include "beavercds-frontend.labels" . | nindent 4 }}

data:
  helm_settings.py: |
    {{- .Values.config | nindent 4 }}
