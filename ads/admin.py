# ads/admin.py
from django.contrib import admin
from .models import Ad, ExchangeProposal


@admin.register(Ad)
class Admin(admin.ModelAdmin):
    list_display = ('title','user', 'category', 'condition', 'created_at')
    list_filter = ('category', 'condition', 'created_at')
    search_fields = ('title', 'description')

@admin.register(ExchangeProposal)
class ExchangeProposalAdmin(admin.ModelAdmin):
    list_display = ('id', 'ad_sender', 'ad_receiver', 'status', 'created_at')
    list_filter = ('status',)