class CostCalculator:
    def __init__(self, price_per_1000_pages):
        self.price_per_1000_pages = price_per_1000_pages

    def estimate_cost(self, num_pages):
        # Cost = (pages / 1000) * price_per_1000_pages
        return (num_pages / 1000.0) * self.price_per_1000_pages

    def print_pricing_info(self):
        print(f"Current OCR pricing: {self.price_per_1000_pages} $ per 1000 pages")
        print("Check for updates at: https://mistral.ai/products/la-plateforme#pricing")