from rest_framework.routers import SimpleRouter

from proxy.views import ActivatedItemView, DeletedItemView, ItemView

router = SimpleRouter()

router.register('activated-item', ActivatedItemView)
router.register('deleted-item', DeletedItemView)
router.register('item', ItemView)

urlpatterns = router.get_urls()
