class Report:
    def __init__(self):
        self.file_reports = []
        self.summary = {}

    def add_file_report(self, file_path, pages, images, est_cost, actual_cost, warnings=None, errors=None):
        self.file_reports.append({
            "file": file_path,
            "pages": pages,
            "images": images,
            "estimated_cost": est_cost,
            "actual_cost": actual_cost,
            "warnings": warnings or [],
            "errors": errors or []
        })

    def generate_summary(self):
        total_files = len(self.file_reports)
        total_pages = sum(r["pages"] for r in self.file_reports)
        total_images = sum(r["images"] for r in self.file_reports)
        total_est_cost = sum(r["estimated_cost"] for r in self.file_reports)
        # total_actual_cost = sum(r["actual_cost"] for r in self.file_reports)  # No longer needed
        self.summary = {
            "total_files": total_files,
            "total_pages": total_pages,
            "total_images": total_images,
            "total_estimated_cost": total_est_cost
        }

    def print_report(self, logger=None):
        for r in self.file_reports:
            msg = (
                f"File: {r['file']}\n"
                f"  Pages: {r['pages']}\n"
                f"  Images: {r['images']}\n"
                f"  Estimated Cost: ${r['estimated_cost']:.4f}\n"
            )
            if r["warnings"]:
                msg += f"  Warnings: {', '.join(r['warnings'])}\n"
            if r["errors"]:
                msg += f"  Errors: {', '.join(r['errors'])}\n"
            if logger:
                logger.info(msg)
            else:
                print(msg)
        self.generate_summary()
        summary_msg = (
            f"Processed {self.summary['total_files']} files, "
            f"{self.summary['total_pages']} pages, "
            f"{self.summary['total_images']} images.\n"
            f"Total Estimated Cost: ${self.summary['total_estimated_cost']:.4f}\n"
        )
        if logger:
            logger.info(summary_msg)
        else:
            print(summary_msg)