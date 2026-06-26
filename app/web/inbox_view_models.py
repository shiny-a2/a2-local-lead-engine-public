from app.core.enums import ReplyClassificationValue

CLASSIFICATION_LABELS_FA = {
    ReplyClassificationValue.POSITIVE_INTEREST: "پاسخ مثبت",
    ReplyClassificationValue.ASKING_PRICE: "درخواست قیمت",
    ReplyClassificationValue.ASKING_DETAILS: "درخواست جزئیات",
    ReplyClassificationValue.REQUESTED_CALL: "درخواست تماس",
    ReplyClassificationValue.NOT_INTERESTED: "عدم علاقه",
    ReplyClassificationValue.ALREADY_HAS_WEBSITE: "وب‌سایت دارد",
    ReplyClassificationValue.WRONG_CONTACT: "تماس اشتباه",
    ReplyClassificationValue.UNSUBSCRIBE_REQUEST: "لغو اشتراک",
    ReplyClassificationValue.OUT_OF_OFFICE: "خارج از دفتر",
    ReplyClassificationValue.BOUNCE_LIKE: "شبیه Bounce",
    ReplyClassificationValue.UNKNOWN_NEEDS_REVIEW: "نیازمند بررسی",
}
