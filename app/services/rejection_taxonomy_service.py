"""Classify WHY an email was rejected so the engine routes it correctly:

  TEXT_FIXABLE    - the words are the problem (unsupported claim, tone, length, generic) ->
                    rewrite the body and re-judge; never burn the lead.
  CONTACT_FIXABLE - the RECIPIENT is the problem (wrong/different business, domain/country/
                    location mismatch, directory address) -> rewriting words can't help and
                    re-sending reworded text to a wrong address is a blunder; route to contact
                    re-discovery instead.
  HARD_BLOCK      - reserved for genuinely unsendable content.

Rule: CONTACT-DOMINANT. If ANY reason looks like a contact/recipient mismatch the whole
rejection is CONTACT_FIXABLE even when text issues co-occur, and an unknown/empty reason set
defaults to CONTACT_FIXABLE (the safe side — we would rather not auto-reword-and-resend)."""

CONTACT_MARKERS = (
    "recipient", "email address", "email does not match", "does not belong", "belongs to",
    "wrong business", "different business", "another business", "same-named", "same name in",
    "not the same entity", "directory", "aggregator", "marketplace", "country", "location",
    "city", "region", "domain does not", "domain mismatch", "different domain", "another company",
)
TEXT_MARKERS = (
    "claim", "unsupported", "evidence", "tone", "exclamation", "length", "word count", "too short",
    "too long", "spam", "promotional", "salesy", "personaliz", "generic", "not specific",
    "relevance", "call to action", "cta", "grammar", "wording", "phrasing", "sentence", "rewrite",
)


class RejectionTaxonomyService:
    def classify(self, reasons: list[str]) -> str:
        blob = " ".join(r.lower() for r in reasons if r).strip()
        if not blob:
            return "CONTACT_FIXABLE"
        if any(marker in blob for marker in CONTACT_MARKERS):
            return "CONTACT_FIXABLE"
        if any(marker in blob for marker in TEXT_MARKERS):
            return "TEXT_FIXABLE"
        return "CONTACT_FIXABLE"

    def classify_judge(self, findings: list[dict]) -> str:
        reasons: list[str] = []
        for finding in findings:
            reasons.append(str(finding.get("finding_type", "")))
            reasons.append(str(finding.get("message", "")))
        return self.classify(reasons)

    def classify_qa(self, issues: list[str]) -> str:
        return self.classify(list(issues))
