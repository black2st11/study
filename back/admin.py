import datetime
from django.contrib import admin
from django.core.exceptions import ValidationError
from django.db.models import Value, F
from django.http import HttpResponseRedirect
from django.urls import reverse, path
from django.utils import timezone
from django.utils.html import format_html

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


class HouseAdminFilter(admin.SimpleListFilter):
    title = '계약'

    parameter_name = 'ownership_category'

    def lookups(self, request, model_admin):
        return (
            ('empty', '세입자 없음'),
            (Ownership.Category.LONG_TERM, '전세'),
            (Ownership.Category.SHORT_TERM, '월세'),
        )

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(ownership_category=self.value())


class HouseAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'get_current_owner', 'get_current_tenant', 'get_current_ownership_category',
        'category', 'post_number', 'address', 'detail_address', 'get_extend_one_year_button'
    ]
    ordering = [
        'id', 'category', 'post_number', 'address', 'detail_address'
    ]
    search_fields = ['category', 'post_number', 'address', 'detail_address', 'current_owner', 'current_tenant']
    actions = ['expire_ownership']
    change_list_template = 'back/house_change_list.html'
    list_filter = [HouseAdminFilter]

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path(
                'extend-ownership-by-days',
                self.admin_site.admin_view(self.extend_ownership_by_days),
                name='extend-ownership-by-days'
            ),
            path(
                '<int:object_id>/extend-one-year',
                self.admin_site.admin_view(self.extend_one_year),
                name='extend-one-year'
            ),
        ]
        dest = urls + my_urls
        return dest

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

    @admin.display(ordering='ownership_category', description='현재 건물 계약상태')
    def get_current_ownership_category(self, obj):
        categories = {
            'empty': '현재 세입자 없음',
            'LongTerm': '전세',
            'ShortTerm': '월세',
        }
        return categories.get(obj.ownership_category)

    @admin.display(description='현재 세입자 1년 연장하기')
    def get_extend_one_year_button(self, obj):
        ownerships = obj.ownerships.filter(
            category__in=[
                Ownership.Category.LONG_TERM,
                Ownership.Category.SHORT_TERM
            ],
            ended__gt=timezone.now(),
        ).order_by('-started')

        if not ownerships:
            return format_html(
                '<span>현재 세입자가 존재하지 않습니다.</a>',
            )

        ownership_pk = ownerships.first().id

        return format_html(
            '<a class="button" href="{}">1년 연장</a>',
            reverse('admin:extend-one-year', args=[ownership_pk])
        )

    @staticmethod
    def extend_one_year(request, object_id):
        try:
            ownership = Ownership.objects.get(id=object_id)
            ownership.ended = ownership.ended + datetime.timedelta(days=365)
            ownership.save()
        except Ownership.DoesNotExist:
            raise ValidationError('Does not exist')
        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))

    @staticmethod
    def extend_ownership_by_days(request):
        categories = {
            'all': [Ownership.Category.LONG_TERM, Ownership.Category.SHORT_TERM],
            'longTerm': [Ownership.Category.LONG_TERM],
            'shortTerm': [Ownership.Category.SHORT_TERM]
        }

        category = request.POST.get('category', None)
        days = request.POST.get('days', None)

        if not (category and days):
            raise ValidationError('현재 요청 주신 데이터가 이상합니다. 확인해주세요.')

        Ownership.objects.filter(
            ended__gt=timezone.now(),
            category__in=categories[category]
        ).update(ended=F('ended') + Value(datetime.timedelta(days=int(days))))

        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/'))


class OwnershipAdmin(admin.ModelAdmin):
    list_display = ['id', 'owner', 'house', 'category', 'amount', 'started', 'ended']
    ordering = ['id', 'owner', 'house', 'category', 'amount', 'started', 'ended']
    search_fields = ['id', 'owner__name', 'house__address', 'category', 'amount', 'started', 'ended']


class PersonAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'age']
    ordering = ['id', 'name', 'age']
    search_fields = ['id', 'name', 'age']


admin.site.register(House, HouseAdmin)
admin.site.register(Ownership, OwnershipAdmin)
admin.site.register(Person, PersonAdmin)
