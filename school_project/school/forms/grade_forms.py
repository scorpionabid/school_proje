from django import forms
from django.utils.translation import gettext_lazy as _
from ..models.grade_models import Grade, Subject

class GradeForm(forms.ModelForm):
    class Meta:
        model = Grade
        fields = [
            'student', 'subject', 'grade_type', 'grade',
            'date', 'semester', 'academic_year', 'note'
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'grade': forms.NumberInput(attrs={'step': '0.5', 'min': '2', 'max': '10'}),
            'note': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        school = kwargs.pop('school', None)
        super().__init__(*args, **kwargs)
        
        if school:
            self.fields['student'].queryset = school.students.filter(is_active=True)
            self.fields['subject'].queryset = Subject.objects.filter(is_active=True)

class GradeFilterForm(forms.Form):
    student = forms.ModelChoiceField(
        queryset=None,
        required=False,
        label=_('Şagird')
    )
    subject = forms.ModelChoiceField(
        queryset=Subject.objects.filter(is_active=True),
        required=False,
        label=_('Fənn')
    )
    grade_type = forms.ChoiceField(
        choices=[('', '----')] + Grade.GRADE_TYPES,
        required=False,
        label=_('Qiymət növü')
    )
    semester = forms.ChoiceField(
        choices=[('', '----'), (1, '1'), (2, '2')],
        required=False,
        label=_('Yarımil')
    )
    start_date = forms.DateField(
        required=False,
        label=_('Başlanğıc tarix'),
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    end_date = forms.DateField(
        required=False,
        label=_('Son tarix'),
        widget=forms.DateInput(attrs={'type': 'date'})
    )

    def __init__(self, *args, **kwargs):
        school = kwargs.pop('school', None)
        super().__init__(*args, **kwargs)
        
        if school:
            self.fields['student'].queryset = school.students.filter(is_active=True)

class GradeBulkCreateForm(forms.Form):
    subject = forms.ModelChoiceField(
        queryset=Subject.objects.filter(is_active=True),
        label=_('Fənn')
    )
    grade_type = forms.ChoiceField(
        choices=Grade.GRADE_TYPES,
        label=_('Qiymət növü')
    )
    date = forms.DateField(
        label=_('Tarix'),
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    semester = forms.ChoiceField(
        choices=[(1, '1'), (2, '2')],
        label=_('Yarımil')
    )
    academic_year = forms.CharField(
        max_length=9,
        label=_('Tədris ili'),
        help_text=_('Məsələn: 2023-2024')
    )
    note = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 3}),
        label=_('Qeyd')
    )

    def __init__(self, *args, **kwargs):
        school = kwargs.pop('school', None)
        class_room = kwargs.pop('class_room', None)
        super().__init__(*args, **kwargs)
        
        if class_room:
            self.fields['students'] = forms.ModelMultipleChoiceField(
                queryset=class_room.students.filter(is_active=True),
                widget=forms.CheckboxSelectMultiple,
                label=_('Şagirdlər')
            )
