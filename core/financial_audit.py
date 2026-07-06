import re
import pandas as pd
from typing import Tuple, List

class FinancialPostAuditor:
    """Executes deterministic verification tests on parsed structures via formula validation gates."""
    
    def execute_deterministic_audit(self, df_healed: pd.DataFrame) -> Tuple[pd.DataFrame, List[pd.DataFrame]]:
        """Parses healed markdown streams back into structured tables and validates matrix formulas."""
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
                
                # Dynamic unicode sanitization and formatting
                for col in ['Qty', 'Net price', 'Gross worth']:
                    temp_df[col] = (
                        temp_df[col]
                        .str.replace(r'\u202f', '', regex=True)  # Strip hidden space fragments
                        .str.replace(' ', '')
                        .str.replace(',', '.')
                        .astype(float)
                    )
                
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