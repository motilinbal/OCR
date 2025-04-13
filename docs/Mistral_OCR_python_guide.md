# 🧑‍💻 Mistral OCR API Developer Guide (Python)

A comprehensive, professional guide to using the Mistral OCR API (`mistral-ocr-latest`) in Python.  
Learn how to set up, authenticate, process PDFs and images, extract structured content, optimize costs, and handle real-world issues.

---

## 🚀 Introduction

Mistral AI offers a powerful Optical Character Recognition (OCR) API that goes beyond simple text extraction.  
Key features:
- **Advanced Layout Understanding**: Handles complex layouts, tables, math, and interleaved images.
- **Multilingual & Multimodal**: Supports thousands of scripts and languages, and extracts embedded images.
- **Speed & Scalability**: Processes up to 2,000 pages/minute.
- **Structured Output**: Returns Markdown (and optionally JSON) preserving document structure.
- **LLM Integration**: Enables querying, summarization, and information extraction.

---

## 1. 🛠️ Setup & Authentication

### 1.1. Account & API Key

1. **Create an account** at [console.mistral.ai](https://console.mistral.ai/).
2. **Activate billing**: Go to Workspace → Billing and add payment info.
3. **Generate an API key**: Go to API Keys, click "Create new key", and copy it securely.
4. **Store your key** as an environment variable (e.g., `MISTRAL_API_KEY`).

### 1.2. Install Python Client

```bash
pip install mistralai python-dotenv datauri
```

### 1.3. Initialize the Client

```python
import os
from mistralai import Mistral
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("MISTRAL_API_KEY")
if not api_key:
    raise ValueError("MISTRAL_API_KEY environment variable not set.")
client = Mistral(api_key=api_key)
print("Mistral client initialized successfully.")
```

---

## 2. 📄 Core OCR Usage

### 2.1. Process a PDF (Local File)

```python
from pathlib import Path

local_pdf_path = Path("your_file.pdf")
if not local_pdf_path.is_file():
    raise FileNotFoundError(f"File not found: {local_pdf_path}")

# 1. Upload file
with open(local_pdf_path, "rb") as f:
    uploaded_file = client.files.upload(
        file={"file_name": local_pdf_path.name, "content": f},
        purpose="ocr"
    )

# 2. Get signed URL
signed_url = client.files.get_signed_url(file_id=uploaded_file.id, expiry=60).url

# 3. Process OCR
ocr_response = client.ocr.process(
    model="mistral-ocr-latest",
    document={"type": "document_url", "document_url": signed_url},
    include_image_base64=True
)
```

### 2.2. Process an Image (Local File)

```python
import base64

local_image_path = Path("your_image.png")
mime_type = "image/png"
with open(local_image_path, "rb") as image_file:
    encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
data_uri = f"data:{mime_type};base64,{encoded_string}"

ocr_response = client.ocr.process(
    model="mistral-ocr-latest",
    document={"type": "image_url", "image_url": data_uri},
    include_image_base64=True
)
```

---

## 3. ⚙️ Request Parameters

| Parameter             | Type         | Required | Description |
|-----------------------|--------------|----------|-------------|
| `model`               | str          | Yes      | Use `"mistral-ocr-latest"` |
| `document`            | dict         | Yes      | PDF or image (see above) |
| `pages`               | list[int]    | No       | 0-based page indices or ranges |
| `include_image_base64`| bool         | No       | Extract images as base64 |
| `image_limit`         | int          | No       | Max images per page |
| `image_min_size`      | int          | No       | Min image size (pixels) |

---

## 4. 📥 Handling the Response

- **Markdown Output**: Each page's content is in `page.markdown`.
- **Images**: If `include_image_base64=True`, images are in `page.images` as base64 strings.
- **Example: Save Markdown and Images**

```python
import base64, os

output_dir = "output"
os.makedirs(output_dir, exist_ok=True)
all_md = ""
for page in ocr_response.pages:
    all_md += f"# Page {page.index}\n\n{page.markdown}\n\n"
    for img in getattr(page, "images", []):
        if hasattr(img, "image_base64") and img.image_base64:
            img_filename = f"img-{img.id}.jpeg"
            with open(os.path.join(output_dir, img_filename), "wb") as f:
                f.write(base64.b64decode(img.image_base64))
with open(os.path.join(output_dir, "output.md"), "w", encoding="utf-8") as f:
    f.write(all_md)
```

---

## 5. 💸 Pricing & Cost Optimization

- **Standard OCR**: ~$1 per 1,000 pages.
- **Batch OCR**: (Not supported for OCR endpoint as of this writing.)
- **Limits**: Max 50MB/file, 1,000 pages/file.
- **Best Practices**:
  - Process only needed pages (use `pages` parameter).
  - Pre-process images for clarity (deskew, enhance contrast).
  - Monitor usage and update pricing in your app as needed.

---

## 6. 🛡️ Error Handling & Troubleshooting

- Use `try...except` to catch `MistralAPIException`, `MistralConnectionException`, and general errors.
- Common issues:
  - **Image placeholder output**: For scanned/image-only PDFs, try improving input quality or use chat completion as a fallback.
  - **401 Unauthorized**: Check API key and billing.
  - **429 Rate Limit**: Implement retries with backoff.
  - **Other**: See [Community Forums](https://stackoverflow.com/questions/tagged/mistral-ai), [Reddit](https://www.reddit.com/r/MistralAI/).

---

## 7. 🧠 Advanced: Document Understanding

- Use the Markdown output as context for chat models (e.g., summarization, Q&A).
- Example: Pass extracted Markdown to `client.chat.complete` for structured extraction.

---

## 8. 📚 Further Resources

- [Official Mistral AI Documentation](https://docs.mistral.ai/)
- [Mistral AI Cookbooks (GitHub)](https://github.com/mistralai/cookbook)
- [Python Client (GitHub)](https://github.com/mistralai/client-python)
- [Setup Instructions](Mistral_OCR_Setup_Instructions.md)

---

## ✅ Summary

- Set up your account, billing, and API key.
- Install the Python client and configure your environment.
- Use `client.ocr.process` for PDFs and images.
- Save Markdown and images from the response.
- Monitor your usage and costs.
- For help, see the links above.

**Happy OCR-ing with Mistral!**
