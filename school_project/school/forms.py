from django import forms
from django.utils.translation import gettext_lazy as _
from .models import School, Student, ClassRoom, Attendance, Grade, Staff
from core.models import CustomUser
from django.contrib.auth.models import User

class SchoolForm(forms.ModelForm):
    class Meta:
        model = School
        fields = [
            'name', 'utis_code', 'school_type', 'sector',
            'address', 'phone', 'email', 'website',
            'language', 'foundation_year', 'shift_count',
            'principal', 'is_active'
        ]
        widgets = {
            'foundation_year': forms.NumberInput(attrs={'min': 1800, 'max': 2100}),
            'shift_count': forms.NumberInput(attrs={'min': 1, 'max': 3}),
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
    """
    İşçi formu
    """
    email = forms.EmailField(label=_('E-poçt'))
    first_name = forms.CharField(label=_('Ad'))
    last_name = forms.CharField(label=_('Soyad'))
    password = forms.CharField(
        label=_('Şifrə'),
        widget=forms.PasswordInput,
        required=False
    )

    class Meta:
        model = Staff
        fields = [
            'staff_type', 'position', 'phone', 'emergency_contact',
            'address', 'education_level', 'specialization',
            'experience_years', 'start_date', 'teaching_subjects',
            'weekly_hours', 'is_active'
        ]
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'teaching_subjects': forms.TextInput(attrs={'placeholder': _('Vergüllə ayıraraq daxil edin')}),
        }

    def __init__(self, *args, **kwargs):
        self.school = kwargs.pop('school', None)
        super().__init__(*args, **kwargs)
        
        if self.instance.pk:
            self.fields['email'].initial = self.instance.user.email
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].disabled = True
            self.fields['password'].help_text = _('Şifrəni dəyişmək üçün doldurun')

    def clean_teaching_subjects(self):
        teaching_subjects = self.cleaned_data.get('teaching_subjects')
        if teaching_subjects:
            return [subject.strip() for subject in teaching_subjects.split(',')]
        return []

    def clean_weekly_hours(self):
        weekly_hours = self.cleaned_data.get('weekly_hours')
        staff_type = self.cleaned_data.get('staff_type')
        
        if staff_type == 'TEACHER' and not weekly_hours:
            raise forms.ValidationError(_('Müəllim üçün həftəlik saat sayı tələb olunur.'))
        elif staff_type != 'TEACHER' and weekly_hours:
            return None
        return weekly_hours

    def save(self, commit=True):
        staff = super().save(commit=False)
        
        if not staff.pk:  # Yeni işçi
            # İstifadəçi yaratma
            user = CustomUser.objects.create(
                username=self.cleaned_data['email'],
                email=self.cleaned_data['email'],
                first_name=self.cleaned_data['first_name'],
                last_name=self.cleaned_data['last_name'],
                is_staff=True
            )
            if self.cleaned_data['password']:
                user.set_password(self.cleaned_data['password'])
            user.save()
            staff.user = user
        else:  # Mövcud işçi
            if self.cleaned_data['password']:
                staff.user.set_password(self.cleaned_data['password'])
            staff.user.first_name = self.cleaned_data['first_name']
            staff.user.last_name = self.cleaned_data['last_name']
            staff.user.save()

        if self.school:
            staff.school = self.school
            
        if commit:
            staff.save()
        return staff

from django.contrib.auth.forms import AuthenticationForm
from .models import SchoolAdmin

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
