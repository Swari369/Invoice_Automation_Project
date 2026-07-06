import os
import pandas as pd
from typing import Dict, List
from config.settings import DIRTY_IMAGES
from core.ocr_engine import OCREngine

class InvoiceExtractor:
    """Handles raw layout scanning and text extraction pipelines from the disk engine."""
    
    def __init__(self, ocr_engine: OCREngine):
        self.engine = ocr_engine

    def extract_clean_batch(self, csv_path: str, folder_path: str, sample_size: int = 5) -> pd.DataFrame:
        """Collects valid target assets and parses layout regions into structured pandas arrays."""
        checklist_df = pd.read_csv(csv_path)
        staging_buffer = []
        
        # Isolate baseline items excluding known stress-test items
        clean_queue = checklist_df[~checklist_df["File Name"].isin(DIRTY_IMAGES)].head(sample_size)
        print(f"\n--- Starting Clean Baseline Run ({len(clean_queue)} files) ---")
        
        for idx, row in clean_queue.iterrows():
            filename = row["File Name"]
            full_path = os.path.join(folder_path, filename)
            
            if not os.path.exists(full_path):
                continue
                
            try:
                result = self.engine.convert_file(full_path)
                if result.document.tables:
                    table_df = result.document.tables[0].export_to_dataframe()
                    table_df["source_invoice"] = filename
                    staging_buffer.append(table_df)
                    print(f"Successfully parsed clean dataframe for: {filename}")
            except Exception as e:
                print(f"Clean parsing failure for {filename}: {e}")
                
        return pd.concat(staging_buffer, ignore_index=True) if staging_buffer else None

    def extract_dirty_markdown_stream(self, folder_path: str, dirty_list: List[str]) -> Dict[str, str]:
        """Extracts text data safely to markdown strings, bypassing dataframe parsing to prevent crashes."""
        dirty_tables_dict = {}
        print(f"\n--- Starting Corrupted Image Stress-Test ({len(dirty_list)} files) ---")
        
        for img_name in dirty_list:
            full_path = os.path.join(folder_path, img_name)
            if not os.path.exists(full_path):
                print(f"Missing stress-test file: {full_path}")
                continue
                
            try:
                print(f"Extracting layout markdown stream from dirty file: {img_name}...")
                result = self.engine.convert_file(full_path)
                dirty_tables_dict[img_name] = result.document.export_to_markdown()
            except Exception as e:
                print(f"Critical layout drop for {img_name}: {e}")
                
        return dirty_tables_dict