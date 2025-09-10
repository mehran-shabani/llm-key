# AGENT_TASKS – محدودهٔ هر ایجنت

## A0: Core & Project
- ساخت اسکلت جنگو: `manage.py`, `project/*`, `settings`, `urls`
- ساخت `core/` برای کد مشترک (client و registry)
- عدم پیاده‌سازی فیچرها
- فایل‌های مجاز: `django_server/project/*`, `django_server/core/*`, `requirements.txt`

## A1: ORM (Prisma → Django)
- اپ `coredb` و همهٔ مدل‌ها طبق `PRISMA_MIGRATION.md`
- Seed به مدیریت‌فرمان
- فایل‌های مجاز: `apps/coredb/*`

## A2: Utils
- تبدیل `server/utils/*` به `apps/common/*`
- فقط OpenAI در AiProviders/EmbeddingEngines/TextToSpeech
- فایل‌های مجاز: `apps/common/*`

## A3: API – Auth/System/Admin
- تبدیل `endpoints/api/auth`, `admin`, `system`
- فایل‌های مجاز: `apps/api_auth/*`, `apps/api_admin/*`, `apps/api_system/*`
- مستندسازی در انکرهای خودش در `API_DOCS.md`

## A4: API – Workspaces/Threads/Chats
- تبدیل `endpoints/api/workspace`, `workspaceThread`, `chats`
- فایل‌های مجاز: `apps/workspaces/*`, `apps/chats/*`

## A5: API – Documents/Files/EmbedManagement
- تبدیل `endpoints/api/document`, `files`, `embedManagement`
- فایل‌های مجاز: `apps/documents/*`, `apps/files/*`

## A6: OpenAI – LLM/Embedding/Image
- LLM: text_gen/text2text
- Embedding: embedding
- Image: image (gpt-image-1)
- فایل‌های مجاز: `apps/llm/*`, `apps/embedding/*`, `apps/image/*`

## A7: STT/TTS
- STT: Whisper
- TTS: OpenAI TTS
- فایل‌های مجاز: `apps/stt/*`, `apps/tts/*`

## A8: Conversation
- زنجیره صوتی طبق `VOICE_CONVERSATION.md`
- فایل‌های مجاز: `apps/conversation/*`

## A9: Swagger → DRF Spectacular
- تبدیل `server/swagger/*` به پیکربندی `schema/` و UI
- فایل‌های مجاز: `apps/api/schema/*`

## A10: Jobs
- تبدیل `server/jobs/*` به `apps/jobs/*` (management commands / APScheduler)
- فایل‌های مجاز: `apps/jobs/*`
