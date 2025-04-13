import os
from dotenv import load_dotenv

class Config:
    def __init__(self, cli_args=None):
        # Load .env file
        load_dotenv()
        self.api_key = os.getenv("MISTRAL_API_KEY")
        self.price_per_1000_pages = float(os.getenv("PRICE_PER_1000_PAGES", "1.0"))
        self.default_output_format = os.getenv("DEFAULT_OUTPUT_FORMAT", "md")
        self.default_log_path = os.getenv("DEFAULT_LOG_PATH", "./output/{basename}/process.log")
        self.default_output_dir = os.getenv("DEFAULT_OUTPUT_DIR", "./output")
        self.default_image_limit = int(os.getenv("DEFAULT_IMAGE_LIMIT", "0"))
        self.default_image_min_size = int(os.getenv("DEFAULT_IMAGE_MIN_SIZE", "0"))

        # CLI overrides
        if cli_args:
            self.apply_cli_overrides(cli_args)

    def apply_cli_overrides(self, cli_args):
        if getattr(cli_args, "output_format", None):
            self.default_output_format = cli_args.output_format
        if getattr(cli_args, "log_path", None):
            self.default_log_path = cli_args.log_path
        if getattr(cli_args, "output_dir", None):
            self.default_output_dir = cli_args.output_dir
        if getattr(cli_args, "image_limit", None):
            self.default_image_limit = cli_args.image_limit
        if getattr(cli_args, "image_min_size", None):
            self.default_image_min_size = cli_args.image_min_size
        if getattr(cli_args, "price_per_1000_pages", None):
            self.price_per_1000_pages = cli_args.price_per_1000_pages

    def validate(self):
        if not self.api_key:
            raise ValueError("MISTRAL_API_KEY is not set in the environment or .env file.")
        if self.price_per_1000_pages <= 0:
            raise ValueError("PRICE_PER_1000_PAGES must be a positive number.")