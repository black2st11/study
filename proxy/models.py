from django.db import models
from django.utils import timezone


class BaseModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    deleted = models.DateTimeField(null=True, blank=True)

    class Meta:
        abstract = True


class ActivatedQuerySet(models.QuerySet):
    def delete(self):
        self.update(deleted=timezone.now())


class ActivatedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted__isnull=True)


class DeletedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(deleted__isnull=False)

    def recover(self):
        return self.update(deleted=None)


class ActivatedActionMixin(models.Model):
    class Meta:
        abstract = True

    def delete(self, *args, **kwargs):
        self.deleted = timezone.now()
        self.save()
        return self


class DeletedActionMixin(models.Model):
    class Meta:
        abstract = True

    def recover(self, *args, **kwargs):
        self.deleted = None
        self.save()
        return self


class Item(BaseModel):
    name = models.CharField(max_length=50)
    price = models.IntegerField()


class ActivatedItem(ActivatedActionMixin, Item):
    objects = ActivatedManager.from_queryset(ActivatedQuerySet)()

    class Meta:
        proxy = True


class DeletedItem(DeletedActionMixin, Item):
    objects = DeletedManager()

    class Meta:
        proxy = True
