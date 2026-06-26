from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core.enums import InboundMatchMethod
from app.db.models.email_send_attempt import EmailSendAttempt
from app.db.models.email_send_queue import EmailSendQueue
from app.db.models.inbound_email_message import InboundEmailMessage
from app.db.models.inbound_thread_match import InboundThreadMatch


class ThreadMatchingService:
    def __init__(self, session: Session):
        self.session = session

    def match(self, message: InboundEmailMessage) -> InboundThreadMatch:
        headers = message.raw_headers_json or {}
        queue_id = headers.get("X-A2-Send-Queue-ID") or headers.get("x-a2-send-queue-id")
        if queue_id and str(queue_id).isdigit():
            queue = self.session.get(EmailSendQueue, int(queue_id))
            if queue:
                return self._store(message, queue, InboundMatchMethod.X_A2_HEADERS, 0.98, False)

        header_blob = " ".join(
            value
            for value in [message.in_reply_to_header, message.references_header]
            if value is not None
        )
        if header_blob:
            attempt = self.session.scalar(
                select(EmailSendAttempt).where(EmailSendAttempt.provider_message_id.is_not(None))
            )
            if attempt and attempt.provider_message_id and attempt.provider_message_id in header_blob:
                queue = self.session.get(EmailSendQueue, attempt.email_send_queue_id)
                if queue:
                    return self._store(message, queue, InboundMatchMethod.MESSAGE_ID_IN_REPLY_TO, 0.9, False)

        queue = self.session.scalar(
            select(EmailSendQueue).where(
                or_(
                    EmailSendQueue.recipient_email == message.from_email,
                    EmailSendQueue.recipient_domain == message.from_email.split("@")[-1],
                )
            )
        )
        if queue:
            return self._store(message, queue, InboundMatchMethod.RECIPIENT_SENDER_MATCH, 0.72, False)

        if message.subject:
            return self._store(message, None, InboundMatchMethod.SUBJECT_SIMILARITY, 0.35, True)
        return self._store(message, None, InboundMatchMethod.UNKNOWN, 0.0, True)

    def _store(
        self,
        message: InboundEmailMessage,
        queue: EmailSendQueue | None,
        method: InboundMatchMethod,
        confidence: float,
        manual: bool,
    ) -> InboundThreadMatch:
        message.matched_send_queue_id = queue.id if queue else None
        message.matched_candidate_business_id = queue.candidate_business_id if queue else None
        row = InboundThreadMatch(
            inbound_message_id=message.id,
            email_send_queue_id=queue.id if queue else None,
            candidate_business_id=queue.candidate_business_id if queue else None,
            match_method=method,
            match_confidence=confidence,
            manual_review_required=manual,
            evidence_json={"method": method.value},
        )
        self.session.add(row)
        self.session.flush()
        return row
