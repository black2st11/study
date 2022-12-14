from django.contrib import admin, messages
from django.utils import timezone
from django.utils.translation import ngettext

from .models import House, Ownership, Person


@admin.action(description='세입자 계약 만료')
def expire_ownership(modeladmin, request, queryset):
    for q in queryset:
        q.ownerships.filter(
            category__in=[
                Ownership.Category.LONG_TERM,
                Ownership.Category.SHORT_TERM
            ]
        ).update(ended=timezone.now())


class HouseAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'get_current_owner', 'get_current_tenant',
        'category', 'post_number', 'address', 'detail_address'
    ]
    ordering = [
        'id', 'category', 'post_number', 'address', 'detail_address'
    ]
    search_fields = ['category', 'post_number', 'address', 'detail_address', 'current_owner', 'current_tenant']
    actions = ['expire_ownership']

    @admin.action(description='세입자 계약 만료')
    def expire_ownership(self, request, queryset):
        for q in queryset:
            q.ownerships.filter(
                category__in=[
                    Ownership.Category.LONG_TERM,
                    Ownership.Category.SHORT_TERM
                ]
            ).update(ended=timezone.now())

    @admin.display(ordering='current_owner', description='현재 건물 주인')
    def get_current_owner(self, obj):
        return obj.current_owner

    @admin.display(ordering='current_tenant', description='현재 건물 세입자')
    def get_current_tenant(self, obj):
        return obj.current_tenant


class OwnershipAdmin(admin.ModelAdmin):
    list_display = ['id', 'owner', 'house', 'category', 'amount', 'started', 'ended']


class PersonAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'age']


admin.site.register(House, HouseAdmin)
admin.site.register(Ownership, OwnershipAdmin)
admin.site.register(Person, PersonAdmin)
