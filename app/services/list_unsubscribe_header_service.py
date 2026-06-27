from email.message import EmailMessage


class ListUnsubscribeHeaderService:
    def add(
        self,
        message: EmailMessage,
        unsubscribe_url: str,
        mailto_email: str | None = None,
        one_click: bool = True,
    ) -> None:
        parts = []
        if mailto_email:
            # Working opt-out that needs no deployed web endpoint (reply/mailto path).
            parts.append(f"<mailto:{mailto_email}?subject=Unsubscribe>")
        if unsubscribe_url:
            parts.append(f"<{unsubscribe_url}>")
        if parts:
            message["List-Unsubscribe"] = ", ".join(parts)
        # Only advertise one-click when the URL endpoint actually accepts the POST.
        if one_click and unsubscribe_url and unsubscribe_url.startswith("http"):
            message["List-Unsubscribe-Post"] = "List-Unsubscribe=One-Click"
