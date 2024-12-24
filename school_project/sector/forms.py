from django import forms
from django.utils.translation import gettext_lazy as _
from documents.models import Document

class ReportForm(forms.ModelForm):
    class Meta:
        model = Document
        fields = ['title', 'description', 'file', 'sector']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['title'].widget.attrs.update({'class': 'form-control'})
        self.fields['description'].widget.attrs.update({'class': 'form-control'})
        self.fields['file'].widget.attrs.update({'class': 'form-control'})
        self.fields['sector'].widget.attrs.update({'class': 'form-control'})

    def clean(self):
        cleaned_data = super().clean()
        cleaned_data['document_type'] = 'REPORT'
        cleaned_data['status'] = 'PENDING'
        return cleaned_data
