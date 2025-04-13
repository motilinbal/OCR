# 🦾 Mistral OCR CLI

A robust, user-friendly command-line tool for extracting text and images from PDFs and images using the Mistral AI OCR API.

---

## 🚀 Features

- **Easy CLI usage**: Process one or many files with a single command.
- **Supports PDFs and images**: Automatic file type detection.
- **Flexible page selection**: Specify page ranges for PDFs.
- **Extracts embedded images**: Saves images found in documents.
- **Customizable output**: Choose Markdown or plain text.
- **Detailed logging**: Console and file logs for every step.
- **Cost estimation**: See your estimated and actual costs per job.
- **Secure API key management**: Never expose your credentials.

---

## 📦 Installation

1. **Clone the repository:**
   ```bash
   git clone <your-repo-url>
   cd <your-repo-directory>
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
   _You will need Python 3.8+._

3. **Set up your environment:**
   - Copy `.env.example` to `.env` and fill in your details, or create `.env` as shown below.

---

## 🛠️ Configuration

Edit the `.env` file in the project root:

```env
MISTRAL_API_KEY=your_key_here
PRICE_PER_1000_PAGES=1.0
DEFAULT_OUTPUT_FORMAT=md
DEFAULT_LOG_PATH=./output/{basename}/process.log
DEFAULT_OUTPUT_DIR=./output
DEFAULT_IMAGE_LIMIT=0
DEFAULT_IMAGE_MIN_SIZE=0
```

- **MISTRAL_API_KEY**: Your secret API key from [Mistral AI](https://console.mistral.ai/).
- **PRICE_PER_1000_PAGES**: The current price in USD for 1,000 pages (see [official pricing](https://mistral.ai/products/la-plateforme#pricing)).
- Other fields control output format, logging, and image extraction.

> **Need help getting your API key?**  
> See [docs/Mistral_OCR_Setup_Instructions.md](docs/Mistral_OCR_Setup_Instructions.md).

---

## 🏃 Usage

```bash
python mistral.py file1.pdf file2.jpg file3.png \
  --output-format md \
  --output-dir ./myresults \
  --log-path ./myresults/process.log \
  --page-ranges 1-3,5,7-9 \
  --image-limit 10 \
  --image-min-size 100
```

### **CLI Options**

- `FILE [FILE ...]`: One or more PDF/image files to process (**required**). List multiple files separated by spaces.
- `--output-format`: `md` (default) or `txt`
- `--output-dir`: Output directory (default: as set in `.env`)
- `--log-path`: Log file path (default: as set in `.env`)
- `--page-ranges`: Page ranges for PDFs, e.g. `1-3,5,7-9`
- `--image-limit`: Max images per page/file
- `--image-min-size`: Minimum image size (pixels)
- `--price-per-1000-pages`: Override price for cost estimation

---

## 📂 Output

- For each input file, a folder named after the file will be created in the output directory.
- Extracted text is saved as `.md` or `.txt`.
- Embedded images are saved as separate files.
- A log file records all steps, warnings, and errors.

---

## 💸 Cost Estimation

- The app estimates your cost before processing and reports the actual cost after.
- Cost is calculated as:  
  `cost = (pages_processed / 1000) * PRICE_PER_1000_PAGES`
- Update your `.env` if Mistral changes their pricing.

---

## 🔒 Security

- **Never share your API key.**
- Store your key securely (see setup instructions).
- `.env` is included in `.gitignore` by default.

---

## 📝 Troubleshooting & Tips

- Make sure billing is active on your Mistral AI account.
- If you see errors about API keys or billing, double-check your `.env` and account status.
- For best results, use high-quality scans/images.
- All warnings and errors are logged for review.

---

## 📖 Documentation

- [Setup Instructions](docs/Mistral_OCR_Setup_Instructions.md)
- [Technical Plan](docs/mistral_ocr_cli_plan.md)
- [Mistral OCR Python Guide](docs/Mistral_OCR_python_guide.md)

---

## 🙏 Acknowledgements

- Built with [Mistral AI](https://mistral.ai/) OCR API.
- See official [Mistral documentation](https://docs.mistral.ai/) for more.

---

## 🦾 Enjoy fast, accurate OCR with full control and transparency!