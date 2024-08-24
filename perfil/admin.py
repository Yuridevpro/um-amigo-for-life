# perfil/admin.py

from django.contrib import admin
from .models import UserProfile

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'nome', 'sobrenome', 'email', 'telefone', 'estado_nome', 'cidade_nome')
    search_fields = ('user__username', 'nome', 'email')
    readonly_fields = ('user', 'nome', 'sobrenome', 'email', 'telefone', 'estado_nome', 'cidade_nome')
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if 'estado_id' in form.base_fields:
            del form.base_fields['estado_id']
        return form

    def get_readonly_fields(self, request, obj=None):
        readonly_fields = super().get_readonly_fields(request, obj)
        # Personalizar os rótulos dos campos somente leitura
        self.model._meta.get_field('estado_nome').verbose_name = 'Estado'
        self.model._meta.get_field('cidade_nome').verbose_name = 'Cidade'
        return readonly_fields

# Registrar o modelo UserProfile com customização
admin.site.register(UserProfile, UserProfileAdmin)
