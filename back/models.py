from django.db import models
from django.db.models import OuterRef
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class HouseQuerySet(models.QuerySet):
    def current_owner(self):
        ownership = Ownership.objects.filter(
            house_id=OuterRef('pk'),
            category=Ownership.Category.BUY,
        ).order_by('-started').values('owner__name')
        return self.annotate(
            current_owner=ownership[:1]
        )

    def current_tenant(self):
        ownership = Ownership.objects.filter(
            house_id=OuterRef('pk'),
            category__in=[Ownership.Category.LONG_TERM, Ownership.Category.SHORT_TERM],
            ended__gt=timezone.now()
        ).order_by('-started').values('owner__name')
        return self.annotate(
            current_tenant=ownership[:1]
        )


class HouseManager(models.Manager):
    def get_queryset(self):
        return HouseQuerySet(self.model).current_tenant().current_owner()


class Person(models.Model):
    name = models.CharField(_('이름'), max_length=50)
    age = models.IntegerField(_('나이'))

    class Meta:
        verbose_name = '사람'
        verbose_name_plural = '사람'

    def __str__(self):
        return f'{self.name}({self.age})'


class House(models.Model):
    class Category(models.TextChoices):
        APARTMENT = 'Apartment', _('아파트')
        House = 'House', _("단독 주책")
        Studio = 'Studio', _('원룸')

    post_number = models.CharField(_('우편 번호'), max_length=10)
    address = models.CharField(_('주소'), max_length=100)
    detail_address = models.CharField(_('상세 주소'), max_length=100)
    category = models.CharField(_('종류'), choices=Category.choices, max_length=50)

    objects = HouseManager()

    class Meta:
        verbose_name = '건물'
        verbose_name_plural = '건물'

    def __str__(self):
        return f"[{self.post_number}] {self.address} 건물"


class Ownership(models.Model):

    class Category(models.TextChoices):
        BUY = 'Buy', _('매매')
        LONG_TERM = 'LongTerm', _('전세')
        SHORT_TERM = 'ShortTerm', _('월세')

    owner = models.ForeignKey(Person, on_delete=models.DO_NOTHING, related_name='ownerships', verbose_name=_('계약 주체'))
    house = models.ForeignKey(House, on_delete=models.DO_NOTHING, related_name='ownerships', verbose_name=_('계약 물건'))
    category = models.CharField(_('종류'), choices=Category.choices, max_length=50)
    amount = models.IntegerField(_('금액'))
    started = models.DateField(_('시작 날짜'))
    ended = models.DateField(_('종료 날짜'), null=True, blank=True)

    class Meta:
        verbose_name = '계약'
        verbose_name_plural = '계약'

    def __str__(self):
        return f'{self.owner.name}의 {self.get_category_display()} 계약'
