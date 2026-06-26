# Email Sending Setup (free, from your own domain)

The engine already has a working SMTP sender (`app/services/cpanel_smtp_provider.py`). It
sends from **your own domain** (`amiraliyaghouti.com`) via cPanel SMTP — free, no credit
card. This is the best option for deliverability and compliance (the unsubscribe domain and
sender identity already point at your domain).

Sending stays **OFF by default**. Everything below only prepares and tests it; no cold email
goes out until you deliberately flip the send flags.

## 1. Get cPanel SMTP credentials

In cPanel → **Email Accounts**, create (or pick) a mailbox, e.g. `hello@amiraliyaghouti.com`,
then open **Connect Devices** to see the SMTP settings. Typical values:

- `SMTP_HOST` = `mail.amiraliyaghouti.com`
- `SMTP_PORT` = `587` (STARTTLS) — the provider calls `starttls()`
- `SMTP_USERNAME` = the full address, e.g. `hello@amiraliyaghouti.com`
- `SMTP_PASSWORD` = that mailbox password

## 2. Put them in `.env`

```env
EMAIL_PROVIDER=cpanel_smtp
SMTP_HOST=mail.amiraliyaghouti.com
SMTP_PORT=587
SMTP_USERNAME=hello@amiraliyaghouti.com
SMTP_PASSWORD=********
SMTP_USE_TLS=true
DEFAULT_FROM_EMAIL=hello@amiraliyaghouti.com
DEFAULT_FROM_NAME=Amirali Yaghouti
DEFAULT_REPLY_TO_EMAIL=hello@amiraliyaghouti.com
UNSUBSCRIBE_TOKEN_SECRET=<a long random string>
```

(Secrets live only in `.env`, never in the database.)

## 3. Check domain deliverability (free, no key)

```bash
.venv/Scripts/python.exe -m app.cli.main send dns-check --domain amiraliyaghouti.com
```

This uses public DNS-over-HTTPS to check SPF / DKIM / DMARC. **Already verified for your
domain:** SPF present, DKIM `default` selector present, DMARC present → `ready_for_cold_email: True`.
(SPF `~all`, DMARC `p=none` is a fine starting posture.)

## 4. Send yourself a test email

```bash
# dry run first (shows what it would do, sends nothing)
.venv/Scripts/python.exe -m app.cli.main send self-test --to you@amiraliyaghouti.com
# actually send the single self-test (only to your own address)
.venv/Scripts/python.exe -m app.cli.main send self-test --to you@amiraliyaghouti.com --commit
```

If you receive it, SMTP works. No lead or campaign data is involved.

## 5. Provider readiness for the pipeline

```bash
.venv/Scripts/python.exe -m app.cli.main send provider-check --provider cpanel_smtp
```

## 6. To actually send campaign emails (deliberate, later)

Real sending stays blocked by multiple gates. Only when you are ready, set:

```env
GLOBAL_OUTREACH_KILL_SWITCH=false
EMAIL_SENDING_ENABLED=true
CONTROLLED_SEND_ENABLED=true
PROVIDER_SEND_ENABLED=true
SEND_PER_RUN_LIMIT=1
SEND_DAILY_LIMIT=3
SEND_WARMUP_MODE=true
```

Then `send build-queue` and `send run --commit` send only approved, in-window, non-suppressed
items. Restore the kill switch after the small send window.

## Free alternatives (also no credit card)

The same `cpanel_smtp` provider is just generic SMTP, so it also works with:

- **Gmail**: `SMTP_HOST=smtp.gmail.com`, port 587, username = your Gmail, password = a Google
  **App Password** (needs 2FA on). Easiest, but weaker for cold-email deliverability.
- **Brevo (Sendinblue)**: free 300/day, no card; use their SMTP host + SMTP key.

Your own domain (above) is recommended over these for trust and unsubscribe alignment.
