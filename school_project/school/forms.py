from django import forms
from django.utils.translation import gettext_lazy as _
from .models import School, Student, ClassRoom, Attendance, Grade, Staff
from core.models import CustomUser
from django.contrib.auth.models import User
from django.contrib.auth.forms import AuthenticationForm
from .models import SchoolAdmin

class SchoolForm(forms.ModelForm):
    class Meta:
        model = School
        fields = [
            'name',
            'utis_code',
            'school_type',
            'language',
            'sector',
            'address',
            'phone',
        ]
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'utis_code': forms.TextInput(attrs={'class': 'form-control'}),
            'school_type': forms.Select(attrs={'class': 'form-control'}),
            'language': forms.Select(attrs={'class': 'form-control'}),
            'sector': forms.Select(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
        }


class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = [
            'first_name', 'last_name', 'father_name',
            'birth_date', 'gender', 'utis_id',
            'class_room', 'admission_date',
            'address', 'phone', 'email',
            'parent_name', 'parent_phone', 'parent_email',
            'is_active'
        ]
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'admission_date': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        self.school = kwargs.pop('school', None)
        super().__init__(*args, **kwargs)
        
        if self.school:
            self.fields['class_room'].queryset = ClassRoom.objects.filter(school=self.school)
        elif self.instance.pk:
            self.fields['class_room'].queryset = ClassRoom.objects.filter(school=self.instance.school)

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.school:
            instance.school = self.school
        if commit:
            instance.save()
        return instance

class ClassRoomForm(forms.ModelForm):
    """
    Sinif formu
    """
    class Meta:
        model = ClassRoom
        fields = [
            'grade', 'division', 'language', 'capacity',
            'current_students', 'class_teacher', 'is_active'
        ]
        widgets = {
            'grade': forms.Select(attrs={'class': 'form-control select2'}),
            'division': forms.TextInput(attrs={'class': 'form-control'}),
            'language': forms.Select(attrs={'class': 'form-control select2'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'max': '40'}),
            'current_students': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'max': '40'}),
            'class_teacher': forms.Select(attrs={'class': 'form-control select2'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }

    def __init__(self, *args, **kwargs):
        self.school = kwargs.pop('school', None)
        super().__init__(*args, **kwargs)
        if self.school:
            self.fields['class_teacher'].queryset = CustomUser.objects.filter(
                staff_profile__school=self.school,
                staff_profile__is_active=True,
                staff_profile__staff_type='TEACHER'
            )
        self.fields['class_teacher'].required = False

    def clean(self):
        cleaned_data = super().clean()
        current_students = cleaned_data.get('current_students')
        capacity = cleaned_data.get('capacity')

        if current_students and capacity and current_students > capacity:
            raise forms.ValidationError(_('Cari şagird sayı tutumdan çox ola bilməz'))

        grade = cleaned_data.get('grade')
        division = cleaned_data.get('division')
        
        if grade and division:
            # Eyni məktəbdə eyni sinif və bölmə olmamalıdır
            if ClassRoom.objects.filter(
                school=self.school if self.school else self.instance.school,
                grade=grade,
                division=division
            ).exclude(pk=self.instance.pk if self.instance else None).exists():
                raise forms.ValidationError(
                    _('Bu sinif və bölmə artıq mövcuddur.')
                )
        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        if self.school:
            instance.school = self.school
        if commit:
            instance.save()
        return instance

class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['student', 'date', 'is_present', 'absence_type', 'note']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        is_present = cleaned_data.get('is_present')
        absence_type = cleaned_data.get('absence_type')
        
        if not is_present and not absence_type:
            raise forms.ValidationError(
                _('Qayıb qeyd edildikdə qayıb növü seçilməlidir.')
            )
        elif is_present and absence_type:
            cleaned_data['absence_type'] = None
            
        return cleaned_data

class GradeForm(forms.ModelForm):
    """
    Qiymət formu
    """
    class Meta:
        model = Grade
        fields = ['student', 'subject', 'grade', 'date', 'note']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'grade': forms.NumberInput(attrs={
                'min': 1,
                'max': 10,
                'class': 'form-control'
            }),
            'student': forms.Select(attrs={'class': 'form-control select2'}),
            'subject': forms.TextInput(attrs={'class': 'form-control'}),
            'note': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'initial' in kwargs and 'grade_type' in kwargs['initial']:
            self.instance.grade_type = kwargs['initial']['grade_type']

class GradeFilterForm(forms.Form):
    """
    Qiymət filtri formu
    """
    student = forms.ModelChoiceField(
        queryset=Student.objects.none(),
        required=False,
        label=_('Şagird'),
        widget=forms.Select(attrs={'class': 'form-control select2'})
    )
    subject = forms.CharField(
        required=False,
        label=_('Fənn'),
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    start_date = forms.DateField(
        required=False,
        label=_('Başlanğıc tarix'),
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )
    end_date = forms.DateField(
        required=False,
        label=_('Son tarix'),
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        school = kwargs.pop('school', None)
        if school:
            self.fields['student'].queryset = Student.objects.filter(
                school=school,
                is_active=True
            )

class StudentFilterForm(forms.Form):
    school = forms.ModelChoiceField(
        queryset=School.objects.all(),
        required=False,
        label=_('Məktəb')
    )
    grade = forms.ChoiceField(
        choices=[(i, str(i)) for i in range(1, 12)],
        required=False,
        label=_('Sinif')
    )
    is_active = forms.BooleanField(
        required=False,
        initial=True,
        label=_('Aktiv')
    )
    search = forms.CharField(
        required=False,
        label=_('Axtar'),
        widget=forms.TextInput(attrs={'placeholder': _('Ad, soyad və ya UTIS ID')})
    )

class AttendanceFilterForm(forms.Form):
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
    is_present = forms.BooleanField(
        required=False,
        label=_('İştirak')
    )
    absence_type = forms.ChoiceField(
        choices=[('', '----')] + Attendance.ABSENCE_TYPES,
        required=False,
        label=_('Qayıb növü')
    )

class StaffForm(forms.ModelForm):
    class Meta:
        model = Staff
        fields = ['first_name', 'last_name', 'email', 'phone', 'position', 'staff_type']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'position': forms.TextInput(attrs={'class': 'form-control'}),
            'staff_type': forms.Select(attrs={'class': 'form-control'}),
        }

class StudentForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ['first_name', 'last_name', 'birth_date', 'gender', 'address', 'phone']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'birth_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'gender': forms.Select(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
        }
class SchoolLoginForm(AuthenticationForm):
    """
    Məktəb admin login formu
    """
    username = forms.CharField(
        widget=forms.TextInput(
            attrs={'class': 'form-control', 'placeholder': _('İstifadəçi adı')}
        )
    )
    password = forms.CharField(
        widget=forms.PasswordInput(
            attrs={'class': 'form-control', 'placeholder': _('Şifrə')}
        )
    )

class SchoolAdminProfileForm(forms.ModelForm):
    """
    Məktəb admin profil formu
    """
    first_name = forms.CharField(
        label=_('Ad'),
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    last_name = forms.CharField(
        label=_('Soyad'),
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        label=_('E-poçt'),
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    phone = forms.CharField(
        label=_('Telefon'),
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = SchoolAdmin
        fields = ['first_name', 'last_name', 'email', 'phone']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email
    
    def save(self, commit=True):
        school_admin = super().save(commit=False)
        
        # User məlumatlarını yenilə
        user = school_admin.user
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        user.save()
        
        if commit:
            school_admin.save()
        
        return school_admin


class ClassRoomForm(forms.ModelForm):
    class Meta:
        model = ClassRoom
        fields = ['grade', 'division', 'capacity']
        widgets = {
            'grade': forms.Select(attrs={'class': 'form-control'}),
            'division': forms.TextInput(attrs={'class': 'form-control'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        }

class AttendanceBulkForm(forms.Form):
    date = forms.DateField(
        label=_('Tarix'),
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    classroom = forms.ModelChoiceField(
        label=_('Sinif'),
        queryset=ClassRoom.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    students = forms.ModelMultipleChoiceField(
        label=_('Şagirdlər'),
        queryset=Student.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'classroom' in self.data:
            try:
                classroom_id = int(self.data.get('classroom'))
                self.fields['students'].queryset = Student.objects.filter(classroom_id=classroom_id)
            except (ValueError, TypeError):
                pass

class GradeForm(forms.ModelForm):
    class Meta:
        model = Grade
        fields = ['student', 'subject', 'grade_type', 'grade', 'date']
        widgets = {
            'student': forms.Select(attrs={'class': 'form-control'}),
            'subject': forms.Select(attrs={'class': 'form-control'}),
            'grade_type': forms.Select(attrs={'class': 'form-control'}),
            'grade': forms.NumberInput(attrs={'class': 'form-control'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
