from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm, UserChangeForm
from django.utils.translation import gettext_lazy as _
from .models import CustomUser

class LoginForm(forms.Form):
    username = forms.CharField(
        label=_('İstifadəçi adı'),
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': _('İstifadəçi adınızı daxil edin')})
    )
    password = forms.CharField(
        label=_('Şifrə'),
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': _('Şifrənizi daxil edin')})
    )

class CustomUserCreationForm(UserCreationForm):
    """
    İstifadəçi yaratma formu
    """
    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'father_name',
                 'user_type', 'utis_code', 'whatsapp_number')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Bütün sahələr üçün Bootstrap class-ları əlavə et
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

    def clean_utis_code(self):
        """
        UTIS kodunun formatını yoxlayır
        """
        utis_code = self.cleaned_data.get('utis_code')
        if utis_code:
            if not utis_code.isdigit() or len(utis_code) != 7:
                raise forms.ValidationError(_('UTIS kodu 7 rəqəmdən ibarət olmalıdır.'))
        return utis_code

class CustomUserChangeForm(UserChangeForm):
    """
    İstifadəçi məlumatlarını dəyişmək üçün form
    """
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'father_name',
                 'user_type', 'utis_code', 'whatsapp_number')
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Bütün sahələr üçün Bootstrap class-ları əlavə et
        for field in self.fields.values():
            field.widget.attrs['class'] = 'form-control'

    def clean_utis_code(self):
        """
        UTIS kodunun formatını yoxlayır
        """
        utis_code = self.cleaned_data.get('utis_code')
        if utis_code:
            if not utis_code.isdigit() or len(utis_code) != 7:
                raise forms.ValidationError(_('UTIS kodu 7 rəqəmdən ibarət olmalıdır.'))
        return utis_code
