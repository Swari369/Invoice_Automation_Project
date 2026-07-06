import os

# Base directory roots
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Centralized Warehouse Paths
# Centralized Warehouse Paths
INVOICE_FOLDER = os.path.join(BASE_DIR, "batch_1", "batch_1", "batch1_1_jpg_invoices")
CSV_TARGET = os.path.join(BASE_DIR, "batch_1", "batch_1", "batch1_1.csv")
OUTPUT_EXCEL = os.path.join(BASE_DIR, "batch1_1_extracted_items.xlsx")

# Targeted Stress-Testing Datasets
DIRTY_IMAGES = [
    "batch1-1.png",
    "batch1-2.jpg",
    "batch1-3.jpg",
    "batch1-4.jpg",
    "batch1-5.jpg"
]

# OpenRouter Global Endpoint Target
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"