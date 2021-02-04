from django import forms
from django_json_widget.widgets import JSONEditorWidget
from .models import LogConsultaEOL


class LogConsultaEOLForm(forms.ModelForm):
    class Meta:
        model = LogConsultaEOL

        fields = ('json',)

        widgets = {
            # choose one mode from ['text', 'code', 'tree', 'form', 'view']
            'json': JSONEditorWidget(mode='form', height='700px', width='100%')

        }
