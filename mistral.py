import sys
from mistral_ocr_cli.cli import main

if __name__ == "__main__":
    # Allow: python mistral.py file1.pdf file2.png --output-format txt ...
    # sys.argv[0] is 'mistral.py', so pass sys.argv[1:] to argparse
    sys.argv[0] = "mistral-ocr"
    main()