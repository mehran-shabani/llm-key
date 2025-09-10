# SERVER_MAP – نگاشت Node/Express به Django/DRF

## پوشه‌ها و مقصد آن‌ها
- `server/endpoints/*` → `apps/api/*` (به چند اپ تقسیم می‌شود: auth, users, workspaces, documents, chats, admin, openai, ...).
- `server/models/*` → مدل‌ها و سرویس‌های دیتابیس در اپ‌های مرتبط (users, workspaces, chats, system, keys, ...).
- `server/prisma/schema.prisma` → تبدیل به مدل‌های Django (بنگر: PRISMA_MIGRATION.md).
- `server/utils/*` → `apps/common/*` (پرونده‌های عمومی مثل logger، http، middleware، validation).  
  - زیرشاخه‌های provider-specific فقط برای **OpenAI** نگه‌داشته شوند؛ بقیه حذف.
- `server/swagger/*` → DRF Spectacular (OpenAPI) در `apps/api/schema/` (Swagger UI).
- `server/storage/*` → `apps/files/` + FileSystemStorage.
- `server/jobs/*` → `apps/jobs/` (management commands یا APScheduler – ساده).
- `server/vectorDbProviders/*` → **حذف کامل** (ما VectorDB چندگانه نمی‌خواهیم).
- `server/EmbeddingEngines/*` → فقط شاخه‌ی `openAi/` تبدیل شود؛ بقیه حذف.
- `server/TextToSpeech/*` → فقط `openAi/`؛ بقیه حذف.

## اصول حذف/ادغام
- هر چیزی که مربوط به Provider غیراز OpenAI باشد حذف.
- Real-time, websocket, streaming حذف.
- ساختار جنگو: اپ‌های مستقل با مرز مشخص + `apps/common` برای یوتیل‌ها.
