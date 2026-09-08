"""Barcha app'larning API URL'lari `/api/` ostida shu yerda yig'iladi.

Har bir app o'z `urls.py` sida router orqali endpoint'larini e'lon qiladi,
bu yerda esa faqat mos prefiks bilan `include` qilinadi.
"""

from django.urls import include, path

urlpatterns = [
    path("audits/", include("apps.core.audits.urls")),
    # ViewSet'lar tayyor bo'lgach quyidagilar ochiladi:
    # path("accounts/", include("apps.accounts.urls")),
    # path("organization/", include("apps.organization.urls")),
    # path("catalog/", include("apps.catalog.urls")),
    # path("warehouse/", include("apps.warehouse.urls")),
    # path("sales/", include("apps.sales.urls")),
    # path("finance/", include("apps.finance.urls")),
    # path("procurement/", include("apps.procurement.urls")),
    # path("hr/", include("apps.hr.urls")),
]
