import os
import re
import time
import base64
import pandas as pd
from openai import OpenAI  # Use the standard OpenAI library to connect to OpenRouter!
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import PdfPipelineOptions, TesseractCliOcrOptions
from docling.document_converter import DocumentConverter, ImageFormatOption

# Initialize your OpenRouter Client
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("GEMINI_API_KEY") # This will grab the key you exported in your terminal
)

# Global Configurations
INVOICE_FOLDER = "batch_1/batch_1/batch1_1_jpg_invoices"
CSV_TARGET = "batch_1/batch_1/batch1_1.csv"
OUTPUT_EXCEL = "batch1_1_extracted_items.xlsx"



DIRTY_IMAGES = [
    "batch1-1.png",
    "batch1-2.jpg",
    "batch1-3.jpg",
    "batch1-4.jpg",
    "batch1-5.jpg"
]

def create_ocr_engine():
    """Configures and initializes the Docling DocumentConverter using local Tesseract CLI."""
    pipeline_options = PdfPipelineOptions()
    pipeline_options.do_ocr = True
    pipeline_options.ocr_options = TesseractCliOcrOptions()

    converter = DocumentConverter(
        format_options={
            InputFormat.IMAGE: ImageFormatOption(pipeline_options=pipeline_options)
        }
    )
    return converter

def extract_clean_invoices(csv_path, folder_path, sample_size=5):
    """Processes clean baseline invoices into native dataframes."""
    checklist_df = pd.read_csv(csv_path)
    converter = create_ocr_engine()
    staging_buffer = []
    
    # Isolate clean files (excluding the dirty stress-test ones)
    clean_queue = checklist_df[~checklist_df["File Name"].isin(DIRTY_IMAGES)].head(sample_size)
    print(f"\n--- Starting Clean Baseline Run ({len(clean_queue)} files) ---")
    
    for idx, row in clean_queue.iterrows():
        filename = row["File Name"]
        full_path = os.path.join(folder_path, filename)
        
        if not os.path.exists(full_path):
            continue
            
        try:
            result = converter.convert(full_path)
            if result.document.tables:
                table_df = result.document.tables[0].export_to_dataframe()
                table_df["source_invoice"] = filename
                staging_buffer.append(table_df)
                print(f"Successfully parsed clean dataframe for: {filename}")
        except Exception as e:
            print(f"Clean parsing failure for {filename}: {e}")
            
    return pd.concat(staging_buffer, ignore_index=True) if staging_buffer else None

def extract_dirty_markdown_stream(folder_path, dirty_list):
    """Processes corrupted/dirty images directly to robust raw markdown text strings."""
    converter = create_ocr_engine()
    dirty_tables_dict = {}
    
    print(f"\n--- Starting Corrupted Image Stress-Test ({len(dirty_list)} files) ---")
    
    for img_name in dirty_list:
        full_path = os.path.join(folder_path, img_name)
        if not os.path.exists(full_path):
            print(f"Missing stress-test file: {full_path}")
            continue
            
        try:
            print(f"Extracting layout markdown stream from dirty file: {img_name}...")
            result = converter.convert(full_path)
            markdown_text = result.document.export_to_markdown()
            dirty_tables_dict[img_name] = markdown_text
        except Exception as e:
            print(f"Critical layout drop for {img_name}: {e}")
            
    return dirty_tables_dict

def run_heuristic_healing(dirty_strings_dict):
    """Applies contextual and formulaic financial rules to repair broken markdown tables."""
    repaired_records = []
    print("\n--- Deploying AI Layout Heuristic Healing Engine ---")
    
    for img_name, raw_ocr_text in dirty_strings_dict.items():
        print(f"Repairing data vectors for: {img_name}...")
        
        repair_prompt = f"""
        You are an advanced financial document parser. The text below represents a corrupted, messy table extraction from a dirty or blurry invoice image ('{img_name}').
        Columns may be smashed together, numbers may be misaligned, or line text might be wrapped onto separate rows awkwardly.

        RAW MESSY TEXT EXTRACTION:
        \"\"\"
        {raw_ocr_text}
        \"\"\"

        YOUR TASK:
        1. Reconstruct this broken extraction into a pristine, beautifully aligned Markdown table.
        2. The output table must explicitly use these exact headers: | Description | Qty | Net price | Gross worth |
        3. Use contextual and mathematical clues to repair structural errors:
           - If a row text wraps to the next line, merge it back into a single clean Description.
           - If Qty and Net price are smashed into one word, separate them logically.
           - Note that Gross worth equals (Qty * Net price * 1.10) due to standard tax. If a number is slightly mangled, use this math rule to infer the correct figure.
        4. Return ONLY the markdown table. Do not include any introductory conversation or text outside the table block.
        """
        
        try:
            # Reverted to standard OpenRouter completion logic
            completion = client.chat.completions.create(
                model="openrouter/free", # Using the free tier model string
                messages=[{"role": "user", "content": repair_prompt}]
            )
            healed_table_markdown = completion.choices[0].message.content
            
            repaired_records.append({
                "Invoice File": img_name,
                "Raw Messy Output": raw_ocr_text,
                "AI Repaired Layout": healed_table_markdown
            })
            time.sleep(1) # Safe API rate bounding
        except Exception as e:
            print(f"AI Healing Layer crashed for {img_name}: {e}")
            
    return pd.DataFrame(repaired_records)

def execute_deterministic_audit(df_healed):
    """Parses healed markdown blocks back into pandas types and checks financial formula boundaries."""
    hitl_review_queue = []
    verified_clean_records = []
    
    print("\n--- Running Programmatic Financial Post-Audit Validation ---")
    
    for idx, row in df_healed.iterrows():
        img_name = row["Invoice File"]
        table_markdown = row["AI Repaired Layout"]
        clean_md = re.sub(r'```markdown|```', '', table_markdown).strip()
        
        try:
            lines = [line.strip() for line in clean_md.split('\n') if line.strip()]
            if len(lines) < 3: 
                raise ValueError("Table payload contains invalid structure sizes.")
                
            headers = [h.strip() for h in lines[0].split('|')[1:-1]]
            data_rows = []
            for l in lines[2:]:
                data_rows.append([val.strip() for val in l.split('|')[1:-1]])
                
            temp_df = pd.DataFrame(data_rows, columns=headers)
            
            # Formating data metrics cleanly
            temp_df['Qty'] = temp_df['Qty'].str.replace(',', '.').astype(float)
            temp_df['Net price'] = temp_df['Net price'].str.replace(',', '.').astype(float)
            temp_df['Gross worth'] = temp_df['Gross worth'].str.replace(',', '.').astype(float)
            
            temp_df['Expected Gross'] = round(temp_df['Qty'] * temp_df['Net price'] * 1.10, 2)
            temp_df['Math Variance'] = abs(temp_df['Gross worth'] - temp_df['Expected Gross'])
            
            failed_rows = temp_df[temp_df['Math Variance'] > 0.05]
            
            if not failed_rows.empty:
                print(f"MATH VARIANCE EXCEPTION: Flagged {img_name}")
                hitl_review_queue.append({
                    "Invoice File": img_name,
                    "Issue": f"Math Variance Found ({len(failed_rows)} invalid items)",
                    "Data": clean_md
                })
            else:
                print(f"AUTO-VERIFIED COMPLIANT: {img_name}")
                temp_df["source_invoice"] = img_name
                verified_clean_records.append(temp_df)
                
        except Exception as e:
            print(f"STRUCTURAL PARSING FAILURE: Flagged {img_name} -> {e}")
            hitl_review_queue.append({
                "Invoice File": img_name,
                "Issue": f"Schema Mapping Error: {str(e)}",
                "Data": table_markdown
            })
            
    return pd.DataFrame(hitl_review_queue), verified_clean_records

if __name__ == "__main__":
    print("=====================================================================")
    print("STARTING AUTOMATED END-TO-END DOCUMENT INTELLIGENCE PIPELINE")
    print("=====================================================================")
    
    # 1. Baseline Run over Standard Clean Assets
    df_clean_extracted = extract_clean_invoices(CSV_TARGET, INVOICE_FOLDER, sample_size=5)
    
    # 2. Stress Test Run over the 5 Corrupted Assets
    dirty_strings = extract_dirty_markdown_stream(INVOICE_FOLDER, DIRTY_IMAGES)
    
    # 3. Process Text Repair via Generative AI
    df_healed_tables = run_heuristic_healing(dirty_strings)
    
    # 4. Filter Results through the Deterministic Verification Layer
    df_hitl_board, clean_records_list = execute_deterministic_audit(df_healed_tables)
    
    # =====================================================================
    # 📋 PRODUCTION MONITORING DASHBOARD OUTPUT
    # =====================================================================
    print("\n" + "="*70)
    print("FINAL SYSTEM PIPELINE METRICS SUMMARY")
    print("="*70)
    print(f"Auto-Verified Clean Batches Consolidated: {len(clean_records_list)}")
    print(f"Exceptions Blocked & Routed to HITL Queue: {len(df_hitl_board)}")
    print("="*70)
    
    if not df_hitl_board.empty:
        print("\nCURRENT HUMAN REVIEW TRIAGE QUEUE:")
        print(df_hitl_board[["Invoice File", "Issue"]].to_string(index=False))
        print("="*70)
    else:
        print("\nAll processed data successfully validated. No outstanding alerts.")