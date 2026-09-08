# Gilam ERP

Gilam sotuvi savdo markazlari uchun ERP tizimi (backend). Django + Django REST
Framework asosidagi API. Ko'p filialli tashkilotlar uchun katalog, ombor, savdo,
moliya, xarid va HR jarayonlarini boshqarishga mo'ljallangan.

## Texnologiyalar

| Qatlam | Vosita |
|---|---|
| Til / runtime | Python 3.12 |
| Framework | Django 5.2, Django REST Framework |
| Ma'lumotlar bazasi | PostgreSQL (PostGIS kerak emas) |
| Autentifikatsiya | JWT — `rest_framework_simplejwt` (access 1 kun, refresh 30 kun) |
| Kesh / navbat | Redis + Celery (`django-celery-beat`) |
| API hujjatlari | `drf-spectacular` (OpenAPI 3) |
| Admin UI | `django-unfold` |
| Audit log | `django-auditlog` |
| Fayl saqlash | Lokal `media/` yoki S3 (`USE_S3=True`) |
| Formatlash | `ruff format` + `ruff check` |

## Talablar

- Python 3.12+
- PostgreSQL 14+ (test bazasi ham PostgreSQL talab qiladi)
- Redis 6+ (kesh — db 2, Celery broker — db 0, natija — db 1)

## O'rnatish

```bash
# 1. Virtual muhit
python3 -m venv .venv
source .venv/bin/activate

# 2. Kutubxonalar
pip install -r requirements.txt

# 3. Muhit sozlamalari
cp .env-example .env
# .env ni tahrirlang — DB_* qiymatlari uchun default yo'q, ular majburiy

# 4. Migratsiyalar
python manage.py migrate

# 5. Superuser (phone_number va full_name so'raladi)
python manage.py createsuperuser

# 6. Ishga tushirish
python manage.py runserver
```

## Muhit o'zgaruvchilari (`.env`)

`django-environ` orqali `config/settings.py` da o'qiladi. Namuna — `.env-example`.

| O'zgaruvchi | Izoh |
|---|---|
| `SECRET_KEY` | Django maxfiy kaliti |
| `DEBUG` | `True` / `False` (default `False`) |
| `ALLOWED_HOSTS` | vergul bilan ajratilgan ro'yxat |
| `DB_NAME`, `DB_USER`, `DB_PASSWORD` | PostgreSQL ulanishi (majburiy) |
| `DB_HOST`, `DB_PORT` | default `localhost:5432` |
| `REDIS_CACHE_URL` | default `redis://127.0.0.1:6379/2` |
| `CELERY_BROKER_URL` | default `redis://127.0.0.1:6379/0` |
| `CELERY_RESULT_BACKEND` | default `redis://127.0.0.1:6379/1` |
| `CORS_ALLOWED_ORIGINS`, `CSRF_TRUSTED_ORIGINS` | frontend domenlari |
| `USE_S3` | `True` bo'lsa media S3'ga yoziladi |
| `AWS_*` | S3 sozlamalari (`USE_S3=True` bo'lganda) |

## Loyiha strukturasi

```
config/           — settings, urls, wsgi/asgi
apps/
├── core/
│   ├── base/     — BaseModel, BaseModelSerializer, BaseViewSet, BaseModelAdmin
│   ├── audits/   — audit log (django-auditlog), faqat o'qish API
│   └── utils/    — renderers/exceptions/throttles (hali settings ga ULANMAGAN)
├── accounts/     — User (phone_number login), Role
├── organization/ — Country, Region, District, Organization, Branch
├── catalog/      — Design, DesignPhoto, ProductColor, ProductParty, Quality, Unit
├── warehouse/    — Warehouse
├── sales/        — (skelet)
├── finance/      — Counterparty, Currency, CurrencyLedger, AccrualRetention
├── procurement/  — (skelet)
└── hr/           — Employee, EmployeeLedger, Position, RecruitmentDismissal, WorkSchedule
```

Har app modular: `models/`, `serializers/`, `views/`, `services/`, `tests/` —
paket ko'rinishida. App label = paket oxirgi segmenti.

### `apps/core/base`

Barcha app shu bazadan meros oladi:

- **`BaseModel`** — UUID `id`, `is_active`, `created_at`, `updated_at`.
  `delete()` → soft delete (`is_active=False`), `hard_delete()` → bazadan o'chiradi.
  `Model.objects.active()` / `.inactive()`.
- **`BaseModelSerializer`** — `is_active` ni javobdan olib tashlaydi;
  `id/created_at/updated_at` read-only; FK/M2M uchun `related_fields`.
- **`BaseManageViewSet`** (CRUD) / **`BaseReadOnlyViewSet`** (faqat o'qish) —
  Swagger tag'i avtomatik; `FullDjangoModelPermissions` (GET uchun ham
  `view_<model>` huquqi kerak).
- **`BaseModelAdmin`** — `django-unfold` + tanlangan yozuvlarni Excel'ga eksport.

## API

- Baza: `/api/`
- Swagger UI: `/api/docs/`
- ReDoc: `/api/redoc/`
- OpenAPI schema: `/api/schema/`

Barcha endpoint default yopiq (`IsAuthenticated`). Hozircha ulangan endpoint:

| Endpoint | Izoh |
|---|---|
| `GET /api/audits/logs/` | Audit log (`?search=`, `?ordering=-timestamp`) |

Qolgan app'larning ViewSet'lari tayyor bo'lgach `apps/urls.py` da ochiladi.

## Celery

```bash
celery -A config worker -l info
celery -A config beat -l info
```

> ⚠️ Hozircha `config/celery.py` yaratilmagan — `settings.py` da `CELERY_*`
> sozlangan, lekin ilova obyekti yo'q. `.delay()` chaqirilsa vazifa bajarilmaydi.

## Testlar

`pytest` ishlatilmaydi — `django.test.TestCase` /
`rest_framework.test.APITestCase` + `APIClient`. Test bazasi ham PostgreSQL.

```bash
python manage.py test
python manage.py test apps.catalog --keepdb
python manage.py test apps.core.audits.tests.LogEntryTestCase.test_list_success
```

- Test nomlash: `test_<harakat>_<kutilgan_natija>`.
- Endpoint testlari uchun: `_success` (2xx), `_invalid_data` (400),
  `_unauthenticated` (401); kerak bo'lsa `_forbidden` (403), `_not_found` (404).
- Mock faqat tashqi servislar uchun (S3, to'lov API, Telegram) — DB va Redis mock qilinmaydi.

## Kod uslubi

- O'zgaruvchi / funksiya / klass nomlari — inglizcha.
- Izoh va docstring — o'zbekcha; xatolik xabarlari — o'zbekcha.
- Har model `Meta` da `db_table` va o'zbekcha `verbose_name` / `verbose_name_plural`.
- `select_related` / `prefetch_related` majburiy — N+1 taqiqlanadi.
- Yangi kutubxona qo'shilganda: `requirements.txt`, `config/settings.py`,
  `.env-example` yangilanadi.

## Ma'lumot manbalari

- `database-structure.txt` — bazaning to'liq sxemasi (DBML).
- `CLAUDE.md` — arxitektura va konvensiyalar bo'yicha batafsil qo'llanma.
