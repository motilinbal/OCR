import logging
import os

class SanitizationWarningFilter(logging.Filter):
    def filter(self, record):
        msg = record.getMessage()
        return not (
            'Extraneous leading bytes detected for image' in msg or
            'No known image signature found for image' in msg
        )

def setup_logger(log_path):
    os.makedirs(os.path.dirname(log_path), exist_ok=True)
    logger = logging.getLogger("mistral_ocr_cli")
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')

    # File handler
    fh = logging.FileHandler(log_path, encoding="utf-8")
    fh.setLevel(logging.INFO)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)
    ch.setFormatter(formatter)
    ch.addFilter(SanitizationWarningFilter())
    logger.addHandler(ch)

    logger.propagate = False
    return logger