import sys
from config.settings import INVOICE_FOLDER, CSV_TARGET, DIRTY_IMAGES
from core.ocr_engine import OCREngine
from core.extractor import InvoiceExtractor
from core.ai_healer import AIHeuristicHealer
from core.financial_audit import FinancialPostAuditor

def run_pipeline():
    print("=====================================================================")
    print("RUNNING MODULAR OBJECT-ORIENTED DOCUMENT INTELLIGENCE SYSTEM")
    print("=====================================================================")
    
    # 1. Dependency Injector Instantiations
    ocr_engine = OCREngine()
    extractor = InvoiceExtractor(ocr_engine)
    ai_healer = AIHeuristicHealer()
    auditor = FinancialPostAuditor()
    
    # 2. Execution Run 1: Standard Clean Extraction
    df_clean_extracted = extractor.extract_clean_batch(CSV_TARGET, INVOICE_FOLDER, sample_size=5)
    
    # 3. Execution Run 2: Stress-Testing String Collection
    dirty_markdown_data = extractor.extract_dirty_markdown_stream(INVOICE_FOLDER, DIRTY_IMAGES)
    
    # 4. Execution Run 3: Generative Data Re-Alignment
    df_healed_tables = ai_healer.heal_corrupted_tables(dirty_markdown_data)
    
    # 5. Execution Run 4: Verification Gatekeeper Audits
    df_hitl_board, clean_records = auditor.execute_deterministic_audit(df_healed_tables)
    
    # =====================================================================
    # 📋 PRODUCTION MONITORING DASHBOARD OUTPUT
    # =====================================================================
    print("\n" + "="*70)
    print("📊 FINAL SYSTEM PIPELINE METRICS SUMMARY")
    print("="*70)
    print(f"Auto-Verified Clean Batches Consolidated: {len(clean_records)}")
    print(f"Exceptions Blocked & Routed to HITL Queue: {len(df_hitl_board)}")
    print("="*70)
    
    if not df_hitl_board.empty:
        print("\nCURRENT HUMAN REVIEW TRIAGE QUEUE:")
        print(df_hitl_board[["Invoice File", "Issue"]].to_string(index=False))
        print("="*70)
    else:
        print("\nAll processed data successfully validated. No outstanding alerts.")

if __name__ == "__main__":
    run_pipeline()