from django.contrib import admin

from proxy.models import Item, DeletedItem, ActivatedItem


def delete_model(modeladmin, request, queryset):
    for item in queryset:
        item.delete()


class ActivateAdmin(admin.ModelAdmin):
    actions = [delete_model]

    def get_queryset(self, request):
        """
        Return a QuerySet of all model instances that can be edited by the
        admin site. This is used by changelist_view.
        """
        qs = self.model.objects.get_queryset()
        # TODO: this should be handled by some parameter to the ChangeList.
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        print(qs)
        return qs

    def delete_queryset(self, request, queryset):
        print(queryset.delete())


admin.site.register(ActivatedItem, ActivateAdmin)
admin.site.register(DeletedItem)
admin.site.register(Item)
