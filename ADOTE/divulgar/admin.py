# admin.py
from django import forms
from django.contrib import admin
from .models import Pet, PetImage

class PetAdminForm(forms.ModelForm):
    cuidados = forms.MultipleChoiceField(
        choices=Pet.choices_cuidados_veterinarios,
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )
    vive_bem_em = forms.MultipleChoiceField(
        choices=Pet.choices_vive_bem_em,
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )
    temperamento = forms.MultipleChoiceField(
        choices=Pet.choices_temperamento,
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )
    sociavel_com = forms.MultipleChoiceField(
        choices=Pet.choices_sociavel_com,
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )

    class Meta:
        model = Pet
        fields = '__all__'

    def clean_cuidados(self):
        return self.cleaned_data.get('cuidados', [])

    def clean_vive_bem_em(self):
        return self.cleaned_data.get('vive_bem_em', [])

    def clean_temperamento(self):
        return self.cleaned_data.get('temperamento', [])

    def clean_sociavel_com(self):
        return self.cleaned_data.get('sociavel_com', [])

class PetImageInline(admin.TabularInline):
    model = PetImage
    extra = 1

class PetAdmin(admin.ModelAdmin):
    form = PetAdminForm
    list_display = ('nome_pet', 'especie', 'sexo', 'tamanho', 'status', 'is_active')
    list_filter = ('status', 'especie', 'tamanho', 'is_active')

admin.site.register(Pet, PetAdmin)
admin.site.register(PetImage)
