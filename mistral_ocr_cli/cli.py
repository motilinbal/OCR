import argparse
import sys
from .config import Config
from .cost import CostCalculator
from .logging import setup_logger
from .ocr_processor import OCRProcessor
from .report import Report
from .utils import parse_page_ranges, get_basename_no_ext

def main():
    parser = argparse.ArgumentParser(description="Mistral OCR CLI")
    parser.add_argument("--input", nargs="+", required=True, help="Input PDF/image files")
    parser.add_argument("--output-format", choices=["md", "txt"], help="Output format (default: md)")
    parser.add_argument("--output-dir", help="Output directory")
    parser.add_argument("--log-path", help="Log file path")
    parser.add_argument("--page-ranges", help="Page ranges, e.g. 1-3,5,7-9")
    parser.add_argument("--image-limit", type=int, help="Max images per page/file")
    parser.add_argument("--image-min-size", type=int, help="Minimum image size (pixels)")
    parser.add_argument("--price-per-1000-pages", type=float, help="Override price per 1000 pages")
    args = parser.parse_args()

    # Load config and apply CLI overrides
    config = Config(cli_args=args)
    try:
        config.validate()
    except Exception as e:
        print(f"Configuration error: {e}")
        sys.exit(1)

    # Set up logger
    first_file = args.input[0]
    basename = get_basename_no_ext(first_file)
    log_path = args.log_path or config.default_log_path.replace("{basename}", basename)
    logger = setup_logger(log_path)
    logger.info("Starting Mistral OCR CLI")

    # Cost calculator
    cost_calc = CostCalculator(config.price_per_1000_pages)
    cost_calc.print_pricing_info()

    # Page ranges
    page_ranges = parse_page_ranges(args.page_ranges) if args.page_ranges else None

    # OCR processor
    ocr = OCRProcessor(config, logger)
    report = Report()

    for file_path in args.input:
        logger.info(f"--- Processing {file_path} ---")
        # Estimate pages (unknown until processed, so estimate = 1 for images, or all pages for PDFs if possible)
        est_pages = 1
        ext = file_path.lower().split(".")[-1]
        if ext == "pdf":
            try:
                import PyPDF2
                with open(file_path, "rb") as f:
                    reader = PyPDF2.PdfReader(f)
                    total_pages = len(reader.pages)
                if page_ranges:
                    est_pages = len(page_ranges)
                else:
                    est_pages = total_pages
            except Exception:
                est_pages = 1
        est_cost = cost_calc.estimate_cost(est_pages)

        # Process file
        result = ocr.process_file(
            file_path=file_path,
            output_dir=args.output_dir or config.default_output_dir,
            output_format=args.output_format or config.default_output_format,
            page_ranges=page_ranges,
            image_limit=args.image_limit or config.default_image_limit,
            image_min_size=args.image_min_size or config.default_image_min_size
        )
        actual_cost = cost_calc.estimate_cost(result["pages"])
        report.add_file_report(
            file_path=file_path,
            pages=result["pages"],
            images=result["images"],
            est_cost=est_cost,
            actual_cost=actual_cost,
            warnings=result["warnings"],
            errors=result["errors"]
        )

    report.print_report(logger=logger)
    logger.info("Mistral OCR CLI finished.")

if __name__ == "__main__":
    main()