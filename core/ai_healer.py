import os
import time
import pandas as pd
from typing import Dict
from openai import OpenAI
from config.settings import OPENROUTER_BASE_URL

class AIHeuristicHealer:
    """Utilizes Context-Aware Large Language Models to structurally heal corrupted layout streams."""
    
    def __init__(self):
        self.client = OpenAI(
            base_url=OPENROUTER_BASE_URL,
            api_key=os.getenv("GEMINI_API_KEY")
        )

    def heal_corrupted_tables(self, dirty_strings_dict: Dict[str, str]) -> pd.DataFrame:
        """Injects heuristic tax boundaries into the model context to reconstruct clean tables."""
        repaired_records = []
        print("\n--- Deploying AI Layout Heuristic Healing Engine ---")
        
        for img_name, raw_ocr_text in dirty_strings_dict.items():
            print(f"Repairing data vectors for: {img_name}...")
            
            repair_prompt = f"""
            You are an advanced financial document parser. Reconstruct this broken extraction into a pristine, beautifully aligned Markdown table.
            The output table must explicitly use these exact headers: | Description | Qty | Net price | Gross worth |
            Note that Gross worth equals (Qty * Net price * 1.10) due to standard tax. If a number is slightly mangled, use this math rule to infer the correct figure.
            Return ONLY the markdown table. Do not include any introductory conversation or text outside the table block.

            RAW MESSY TEXT EXTRACTION:
            \"\"\"
            {raw_ocr_text}
            \"\"\"
            """
            
            try:
                completion = self.client.chat.completions.create(
                    model="openrouter/free",
                    messages=[{"role": "user", "content": repair_prompt}]
                )
                healed_table_markdown = completion.choices[0].message.content
                
                repaired_records.append({
                    "Invoice File": img_name,
                    "Raw Messy Output": raw_ocr_text,
                    "AI Repaired Layout": healed_table_markdown
                })
                time.sleep(1)  # Safe API rate bounding
            except Exception as e:
                print(f"AI Healing Layer crashed for {img_name}: {e}")
                
        return pd.DataFrame(repaired_records)