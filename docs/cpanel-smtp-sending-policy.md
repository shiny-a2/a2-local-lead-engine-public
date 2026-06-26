# cPanel SMTP Sending Policy

cPanel SMTP is an MVP provider option. SMTP acceptance is recorded as `SENT_TO_PROVIDER`, not delivered. Inbox delivery remains unknown unless future bounce/reply handling proves otherwise.

Credentials are read from env only and never logged or stored in DB.
