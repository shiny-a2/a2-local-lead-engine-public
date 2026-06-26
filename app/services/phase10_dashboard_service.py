from app.core.enums import EmailSendQueueStatus

FA_STATUS = {
    EmailSendQueueStatus.READY_TO_SEND_CONTROLLED.value: "آماده ارسال کنترل‌شده",
    EmailSendQueueStatus.SEND_DRY_RUN_PLANNED.value: "برنامه‌ریزی‌شده در حالت آزمایشی",
    EmailSendQueueStatus.BLOCKED_BY_GLOBAL_KILL_SWITCH.value: "بلاک‌شده به دلیل خاموش بودن ارسال",
    EmailSendQueueStatus.BLOCKED_BY_SUPPRESSION.value: "بلاک‌شده به دلیل لیست عدم ارسال",
    EmailSendQueueStatus.BLOCKED_BY_DAILY_LIMIT.value: "بلاک‌شده به دلیل محدودیت روزانه",
    EmailSendQueueStatus.BLOCKED_BY_PROVIDER_CONFIG.value: "بلاک‌شده به دلیل تنظیمات فرستنده",
    EmailSendQueueStatus.BLOCKED_DUPLICATE_SEND.value: "بلاک‌شده به دلیل ارسال تکراری",
    EmailSendQueueStatus.BLOCKED_BY_SEND_WINDOW.value: "بلاک‌شده به دلیل خارج بودن از بازه مجاز ارسال",
    EmailSendQueueStatus.BLOCKED_BY_PROVIDER_CIRCUIT_BREAKER.value: "بلاک‌شده به دلیل مدار باز سرویس‌دهنده",
    EmailSendQueueStatus.HELD_BY_OPERATOR.value: "نگه‌داشته‌شده توسط اپراتور",
    EmailSendQueueStatus.CANCELLED_BY_OPERATOR.value: "لغوشده توسط اپراتور",
    EmailSendQueueStatus.SENDING.value: "در حال ارسال",
    EmailSendQueueStatus.SENT_TO_PROVIDER.value: "ارسال‌شده به سرویس‌دهنده",
    EmailSendQueueStatus.FAILED_SMTP_ERROR.value: "خطای SMTP",
}


class Phase10DashboardService:
    def status_fa(self, status: str) -> str:
        return FA_STATUS.get(status, status)
