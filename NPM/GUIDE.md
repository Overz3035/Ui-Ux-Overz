# راهنمای uiux-overz — نصب اسکیل‌های UIUX ENGINE با یک دستور

## کاربر هستی؟ (می‌خوای اسکیل‌ها رو روی پروژه‌ات نصب کنی)

فقط این یک خط را داخل پوشه‌ی پروژه‌ات بزن — بدون GitHub، بدون زیپ، حدود ۷۵۸KB دانلود:

```bash
npx uiux-overz init
```

| آپشن | کار |
|---|---|
| `npx uiux-overz init` | نصب کامل: ۴۶ اسکیل + بایندر + پوشه مدیا + gitignore + AGENTS.md |
| `npx uiux-overz init --minimal` | فقط بایندر (بدون کپی ۴۶ اسکیل) |
| `npx uiux-overz init --dir ./my-app` | نصب روی پوشه‌ای دیگر |
| `npx uiux-overz --help` | راهنما |

### بعد از نصب چه چیزی ساخته می‌شود؟

| مسیر | کاربرد |
|---|---|
| `.agents/skills/*` | هر ۴۶ اسکیل (motion، design، workflow) |
| `.agents/skills/uiux-engine/SKILL.md` | قرارداد اصلی پروژه |
| `.claude/skills/uiux-engine/SKILL.md` | اتصال Claude Code |
| `.kilo/command/uiux.md` | دستور `/uiux` در Kilo Code |
| `AGENTS.md` (بلاک managed) | قوانین ایجنت‌ها — بین مارکرها دست نبر |
| `INBOX-OverzStyleUIUX/images/` و `videos/` | پوشه عکس و فیلم پروژه (فعلاً خالی + `.gitkeep`) |
| `.gitignore` | قانون سبک نگه‌داشتن مدیا (خودکار اضافه می‌شود) |

اجرای دوباره‌ی `init` امن است (idempotent) — چیزی را خراب یا تکراری نمی‌کند.

### قانون مدیا

محتوای `videos/*` و `images/*` کامیت نمی‌شود (فقط `.gitkeep` می‌ماند) تا حجم repo بالا نرود.
اگر خواستی عکسی واقعاً کامیت شود، آن را از قانون `.gitignore` مستثنی کن.

---

## نگه‌دارنده‌ی پکیج هستی؟ (آپدیت و انتشار نسخه جدید)

```powershell
cd NPM
# ۱. اسکیل‌ها را در .agents/skills تغییر بده
# ۲. ورژن را ببر بالا + ثابت VERSION در bin/uiux-overz.js را هم همان عدد کن
npm version patch     # باگ‌فیکس → 1.0.1 | فیچر جدید: npm version minor
# ۳. انتشار (توکن granular با Bypass 2FA لازم است، یک‌بار در npmconfig ست شده)
npm publish
# ۴. تایید
npm view uiux-overz version
```

- payload موقع `prepack` خودکار از `.agents/skills/` ساخته می‌شود — `NPM/payload/` کامیت نمی‌شود.
- عکس/فیلم/INDEX هیچ‌وقت داخل پکیج نمی‌رود (whitelist در `files` داخل `package.json`).
- ورژن تکراری publish نمی‌شود — همیشه اول `npm version` بزن.

## خطاهای رایج

| خطا | راه‌حل |
|---|---|
| `403 ... Two-factor ... required` | توکن granular با Bypass 2FA بساز و `npm config set //registry.npmjs.org/:_authToken TOKEN` |
| `Select at least organization` در فرم توکن | Packages → **All packages**، Organizations → **No access** |
| `You cannot publish over previously published version` | اول `npm version patch` |
| `ENEEDAUTH` | `npm login` |
| `E404` در `npm view` | هنوز publish نشده یا اسم اشتباه است |

صفحه پکیج: **npmjs.com/package/uiux-overz**
