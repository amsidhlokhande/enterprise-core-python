"""
PII (Personally Identifiable Information) Masking Filter for Enterprise Python Logging.
"""
import re
import logging

class PIIMaskingFilter(logging.Filter):
    """
    Scrubs sensitive PII (emails, payment cards, account numbers, bearer tokens, API keys)
    from all log records before output.
    """
    EMAIL_REGEX = re.compile(r'([a-zA-Z0-9_.+-]+)@([a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+)')
    CARD_REGEX = re.compile(r'\b(?:\d{4}[ -]?){3}\d{4}\b')
    ACCOUNT_REGEX = re.compile(r'\b\d{9,18}\b')
    BEARER_REGEX = re.compile(r'(Bearer\s+)[A-Za-z0-9\-._~+/]+=*', re.IGNORECASE)

    def mask_text(self, text: str) -> str:
        if not isinstance(text, str):
            return text
        text = self.EMAIL_REGEX.sub(r'\1[at]***.com', text)
        text = self.CARD_REGEX.sub(r'****-****-****-XXXX', text)
        text = self.ACCOUNT_REGEX.sub(r'***ACCOUNT***', text)
        text = self.BEARER_REGEX.sub(r'\1[REDACTED_TOKEN]', text)
        return text

    def filter(self, record: logging.LogRecord) -> bool:
        if isinstance(record.msg, str):
            record.msg = self.mask_text(record.msg)
        if isinstance(record.args, dict):
            record.args = {k: self.mask_text(v) if isinstance(v, str) else v for k, v in record.args.items()}
        elif isinstance(record.args, (list, tuple)):
            record.args = tuple(self.mask_text(v) if isinstance(v, str) else v for v in record.args)
        return True
