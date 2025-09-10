# PRISMA_MIGRATION – از Prisma به Django ORM

## گام‌ها
1. `schema.prisma` را منبع حقیقت در نظر بگیر.
2. برای هر مدل Prisma یک مدل Django بساز؛ نام‌ها را PascalCase نگه‌دار، جدول را با `db_table` هم‌نام کن.
3. Index/Unique‌ها را با `Meta.indexes` و `unique_together`/`UniqueConstraint` اعمال کن.
4. روابط:
   - `@relation(fields: [xId], references: [id])` → `ForeignKey('App.Model', on_delete=...)`
   - `many-to-many` → `ManyToManyField` با جدول واسط اگر Prisma چنین چیزی دارد.
5. انواع:
   - `String` → `CharField/TextField` (براساس طول)
   - `Int/BigInt` → `IntegerField/BigIntegerField`
   - `Float/Decimal` → `FloatField/DecimalField`
   - `Boolean` → `BooleanField`
   - `DateTime` → `DateTimeField`
   - `Json` → `JSONField`
6. مقدارهای پیش‌فرض Prisma را به `default=` منتقل کن.
7. Seedهای `seed.js` را به مدیریت‌فرمان ساده در `apps/coredb/management/commands/seed.py` تبدیل کن.

## خروجی
- اپ `coredb` شامل همهٔ مدل‌های دیتابیس مشترک.
- مهاجرت‌ها با `makemigrations` تولید شوند.
