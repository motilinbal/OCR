import os
import base64
from pathlib import Path
from mistralai import Mistral
# Exception handling: Try to import as in the official guide, fallback to Exception if not present.
# See docs/Mistral_OCR_python_guide.md and mistralai 1.6.0 package structure.
try:
    from mistralai import MistralAPIException, MistralConnectionException
except ImportError:
    MistralAPIException = Exception
    MistralConnectionException = Exception
from .utils import ensure_dir_exists, get_basename_no_ext, format_exception

def detect_image_extension(image_bytes):
    if image_bytes.startswith(b'\xFF\xD8\xFF'):
        return '.jpeg'
    elif image_bytes.startswith(b'\x89PNG\r\n\x1a\n'):
        return '.png'
    elif image_bytes.startswith(b'GIF87a') or image_bytes.startswith(b'GIF89a'):
        return '.gif'
    elif image_bytes.startswith(b'BM'):
        return '.bmp'
    else:
        return '.bin'  # Unknown format
import hashlib

def sanitize_image_bytes(image_bytes, logger=None, max_scan=64, img_id=None, raw_base64=None):
    """
    If image_bytes does not start with a known image signature, scan the first max_scan bytes
    for a known signature. If found, strip leading bytes and return the corrected bytes.
    Log a warning if correction is applied, including image id, offset, and a hash/snippet of the raw base64 string.
    """
    signatures = [
        (b'\xFF\xD8\xFF', '.jpeg'),
        (b'\x89PNG\r\n\x1a\n', '.png'),
        (b'GIF87a', '.gif'),
        (b'GIF89a', '.gif'),
        (b'BM', '.bmp'),
    ]
    for sig, _ in signatures:
        if image_bytes.startswith(sig):
            return image_bytes  # Already correct
    # Scan for signature
    for offset in range(1, max_scan):
        for sig, _ in signatures:
            if image_bytes[offset:offset+len(sig)] == sig:
                if logger:
                    b64_hash = hashlib.sha256(raw_base64.encode('utf-8')).hexdigest()[:12] if raw_base64 else "N/A"
                    logger.warning(
                        f"Extraneous leading bytes detected for image {img_id} (offset {offset}); "
                        f"stripping for valid image signature {sig.hex()}. "
                        f"Base64 hash: {b64_hash} | Base64 head: {raw_base64[:24] if raw_base64 else 'N/A'}"
                    )
                return image_bytes[offset:]
    if logger:
        b64_hash = hashlib.sha256(raw_base64.encode('utf-8')).hexdigest()[:12] if raw_base64 else "N/A"
        logger.warning(
            f"No known image signature found for image {img_id}. Saving as .bin. "
            f"Base64 hash: {b64_hash} | Base64 head: {raw_base64[:24] if raw_base64 else 'N/A'}"
        )
    return image_bytes  # No correction possible


class OCRProcessor:
    def __init__(self, config, logger):
        self.config = config
        self.logger = logger
        self.client = Mistral(api_key=config.api_key)

    def process_file(self, file_path, output_dir, output_format="md", page_ranges=None, image_limit=None, image_min_size=None):
        ext = os.path.splitext(file_path)[1].lower()
        basename = get_basename_no_ext(file_path)
        file_output_dir = os.path.join(output_dir, basename)
        ensure_dir_exists(file_output_dir)
        log = self.logger

        try:
            if ext in [".pdf"]:
                # Upload PDF, get signed URL
                with open(file_path, "rb") as f:
                    uploaded_file = self.client.files.upload(
                        file={"file_name": os.path.basename(file_path), "content": f},
                        purpose="ocr"
                    )
                signed_url_response = self.client.files.get_signed_url(file_id=uploaded_file.id, expiry=60)
                document = {"type": "document_url", "document_url": signed_url_response.url}
            elif ext in [".png", ".jpg", ".jpeg", ".bmp", ".tiff"]:
                # Encode image as base64 data URI
                mime_type = f"image/{ext[1:] if ext != '.jpg' else 'jpeg'}"
                with open(file_path, "rb") as image_file:
                    encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                data_uri = f"data:{mime_type};base64,{encoded_string}"
                document = {"type": "image_url", "image_url": data_uri}
            else:
                raise ValueError(f"Unsupported file type: {ext}")

            # Prepare OCR parameters
            ocr_kwargs = {
                "model": "mistral-ocr-latest",
                "document": document,
                "include_image_base64": True
            }
            if page_ranges:
                ocr_kwargs["pages"] = page_ranges
            if image_limit:
                ocr_kwargs["image_limit"] = image_limit
            if image_min_size:
                ocr_kwargs["image_min_size"] = image_min_size

            log.info(f"Processing file: {file_path}")
            ocr_response = self.client.ocr.process(**ocr_kwargs)
            log.info("OCR processing successful.")

            # Extract and save markdown
            all_markdown_content = ""
            images_saved = 0
            pages_processed = 0
            # Map of old image filename to new filename (with extension)
            image_filename_map = {}

            for page in getattr(ocr_response, "pages", []):
                pages_processed += 1
                all_markdown_content += f"# Page {page.index}\n\n{page.markdown}\n\n"
                # Save images
                if hasattr(page, "images") and page.images:
                    for img in page.images:
                        if hasattr(img, "image_base64") and img.image_base64:
                            # Decode base64
                            try:
                                image_bytes = base64.b64decode(img.image_base64)
                            except Exception as e:
                                self.logger.error(f"Failed to decode base64 for image {img.id}: {e}")
                                continue
                            # Sanitize for extraneous leading bytes
                            image_bytes = sanitize_image_bytes(
                                image_bytes,
                                logger=self.logger,
                                img_id=getattr(img, "id", "unknown"),
                                raw_base64=img.image_base64
                            )
                            # Detect extension
                            ext = detect_image_extension(image_bytes)
                            if ext == '.bin':
                                self.logger.warning(f"Unknown image format for image {img.id}, saving as .bin")
                            # Compose new filename
                            img_filename = f"{img.id}{ext}"
                            img_path = os.path.join(file_output_dir, img_filename)
                            with open(img_path, "wb") as img_f:
                                img_f.write(image_bytes)
                            images_saved += 1
                            # Track mapping for markdown update
                            # The markdown likely references e.g. img-1.jpeg, but the old code used img.id (no ext)
                            # We'll replace all occurrences of the old reference with the new one
                            # Try both with and without .jpeg for robustness
                            image_filename_map[f"{img.id}"] = img_filename
                            image_filename_map[f"{img.id}.jpeg"] = img_filename
                            image_filename_map[f"{img.id}.jpg"] = img_filename

            # Update markdown image references to use correct filenames
            for old, new in image_filename_map.items():
                all_markdown_content = all_markdown_content.replace(f"({old})", f"({new})").replace(f'src="{old}"', f'src="{new}"')

            # Save markdown or txt
            output_file = os.path.join(file_output_dir, f"{basename}.{output_format}")
            with open(output_file, "w", encoding="utf-8") as f:
                if output_format == "md":
                    f.write(all_markdown_content)
                else:
                    # Convert markdown to plain text (simple strip)
                    f.write(all_markdown_content.replace("#", "").replace("*", ""))

            log.info(f"Saved output to {output_file} (pages: {pages_processed}, images: {images_saved})")
            return {
                "pages": pages_processed,
                "images": images_saved,
                "output_file": output_file,
                "warnings": [],
                "errors": []
            }
        except (MistralAPIException, MistralConnectionException, Exception) as e:
            log.error(f"OCR failed for {file_path}: {format_exception(e)}")
            return {
                "pages": 0,
                "images": 0,
                "output_file": None,
                "warnings": [],
                "errors": [format_exception(e)]
            }