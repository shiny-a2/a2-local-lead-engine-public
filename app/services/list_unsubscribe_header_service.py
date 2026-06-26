from email.message import EmailMessage


class ListUnsubscribeHeaderService:
    def add(self, message: EmailMessage, unsubscribe_url: str) -> None:
        message["List-Unsubscribe"] = f"<{unsubscribe_url}>"
        message["List-Unsubscribe-Post"] = "List-Unsubscribe=One-Click"
