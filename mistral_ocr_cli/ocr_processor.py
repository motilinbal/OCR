import os
import base64
from pathlib import Path
from mistralai import Mistral
from mistralai.exceptions import MistralAPIException, MistralConnectionException
from .utils import ensure_dir_exists, get_basename_no_ext, format_exception

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
            for page in getattr(ocr_response, "pages", []):
                pages_processed += 1
                all_markdown_content += f"# Page {page.index}\n\n{page.markdown}\n\n"
                # Save images
                if hasattr(page, "images") and page.images:
                    for img in page.images:
                        if hasattr(img, "image_base64") and img.image_base64:
                            img_filename = f"img-{img.id}.jpeg"
                            img_path = os.path.join(file_output_dir, img_filename)
                            with open(img_path, "wb") as img_f:
                                img_f.write(base64.b64decode(img.image_base64))
                            images_saved += 1

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