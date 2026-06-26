# راه‌اندازی ایمیل روی سی‌پنل (گام‌به‌گام)

هدف: آماده‌سازی صندوق `info@amiraliyaghouti.com` برای ارسال. تا وقتی خودت تصمیم نگیری،
ارسالِ واقعیِ کمپین خاموش می‌ماند؛ این مرحله فقط آماده‌سازی و تست است.

## گام ۱ — ورود به سی‌پنل
از طریق پنل میزبانت وارد سی‌پنل شو (آدرسی شبیه زیر):

```
https://amiraliyaghouti.com:2083
```

## گام ۲ — ساخت صندوق ایمیل
در بخش «Email Accounts» یک حساب با این آدرس و یک رمز قوی بساز:

```
info@amiraliyaghouti.com
```

## گام ۳ — گرفتن تنظیمات ارسال
روی همان حساب گزینهٔ «Connect Devices» را باز کن. این مقادیر را لازم داریم:

```
سرور ارسال (SMTP) : mail.amiraliyaghouti.com
پورت              : 587
رمزگذاری          : STARTTLS
نام کاربری        : info@amiraliyaghouti.com
رمز               : همان رمزی که در گام ۲ ساختی
```

## گام ۴ — بررسی تحویل‌پذیری
بخش «Email Deliverability» را باز کن و مطمئن شو برای دامنه‌ات SPF و DKIM سبز (Valid)
هستند. اگر دکمهٔ «Repair» دیدی، بزن. (بررسیِ خودکارِ ما نشان داد دامنه‌ات از قبل
SPF و DKIM و DMARC دارد و آماده است.)

## گام ۵ — گذاشتن رمز در تنظیمات و تست
وقتی صندوق ساخته شد، این خط‌ها را به فایل تنظیمات (فایل `.env`) اضافه کن (یا رمز را به
من بده تا اضافه کنم):

```
SMTP_HOST=mail.amiraliyaghouti.com
SMTP_PORT=587
SMTP_USERNAME=info@amiraliyaghouti.com
SMTP_PASSWORD=رمزِ_صندوق
SMTP_USE_TLS=true
```

سپس یک ایمیل آزمایشی فقط به خودت می‌فرستیم (به هیچ کسب‌وکاری کاری ندارد):

```
.venv/Scripts/python.exe -m app.cli.main send self-test --to info@amiraliyaghouti.com --commit
```

اگر ایمیل به دستت رسید، یعنی ارسال درست کار می‌کند.
