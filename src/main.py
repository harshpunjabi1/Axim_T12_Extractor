import pandas as pd
import numpy as np
from pathlib import Path

# GITHUB READY: Uses relative paths so it runs on any machine
BASE_DIR = Path.cwd()
INPUT_PATH = BASE_DIR / "data" / "input"
OUTPUT_PATH = BASE_DIR / "data" / "output"
OUTPUT_PATH.mkdir(parents=True, exist_ok=True)

def clean_val(x):
    if pd.isna(x) or str(x).strip() in ['', '-', '—', 'None']: return 0.0
    s = str(x).replace('$', '').replace(',', '').strip()
    if '(' in s and ')' in s: s = '-' + s.replace('(', '').replace(')', '')
    elif s.endswith('-'): s = '-' + s[:-1]
    try: return float(s)
    except: return 0.0

def get_best_label(row, data_start_col):
    left_side = row[:data_start_col]
    text_cells = [str(x).strip() for x in left_side if len(str(x).strip()) > 1]
    if not text_cells: return ""
    return max(text_cells, key=len)

def process_t12(file_path):
    print(f"Processing: {file_path.name}")
    df = pd.read_csv(file_path, header=None).fillna('') if file_path.suffix == '.csv' else pd.read_excel(file_path, header=None).fillna('')
    
    num_mat = df.applymap(clean_val).values
    col_counts = np.count_nonzero(num_mat, axis=0)
    best_start = 0
    max_hits = 0
    for c in range(num_mat.shape[1] - 11):
        score = np.sum(col_counts[c:c+12])
        if score > max_hits:
            max_hits = score
            best_start = c
            
    data_grid = num_mat[:, best_start:best_start+12]
    row_sums = np.sum(data_grid, axis=1)
    is_total = np.zeros(len(df), dtype=bool)
    # AUDIT TRAIL: Track why a row was removed
    audit_trail = ["Layer 1 Item"] * len(df)

    for i in range(len(df)):
        target = row_sums[i]
        if abs(target) < 0.01: continue
        
        for j in range(max(0, i - 200), i):
            active_leaves = [k for k in range(j, i) if not is_total[k] and abs(row_sums[k]) > 0.01]
            if not active_leaves: continue
            
            leaf_vals = [row_sums[k] for k in active_leaves]
            if np.isclose(target, np.sum(leaf_vals), atol=0.5):
                is_total[i] = True
                audit_trail[i] = f"Pruned: Subtotal of rows {active_leaves[0]}-{active_leaves[-1]}"
                break
            
            for p in range(1, len(leaf_vals)):
                if np.isclose(target, np.sum(leaf_vals[:p]) - np.sum(leaf_vals[p:]), atol=0.5) or \
                   np.isclose(target, np.sum(leaf_vals[p:]) - np.sum(leaf_vals[:p]), atol=0.5):
                    is_total[i] = True
                    audit_trail[i] = "Pruned: Net Calculation (NOI)"
                    break
            if is_total[i]: break

    extracted = []
    for i in range(len(df)):
        label = get_best_label(df.iloc[i].values, best_start)
        # REFINED: Keep row if it's NOT a total and HAS a label (even if values are 0)
        if not is_total[i] and label:
            row_dict = {"Account": label, "Status": audit_trail[i], "Source_Row": i}
            for m in range(12):
                row_dict[f"Month_{m+1}"] = data_grid[i, m]
            row_dict["Total"] = row_sums[i]
            extracted.append(row_dict)

    if extracted:
        out_df = pd.DataFrame(extracted)
        out_df.to_csv(OUTPUT_PATH / f"L1_{file_path.stem}.csv", index=False)
        print(f"  ✓ {len(out_df)} rows saved.")

if __name__ == "__main__":
    for f in INPUT_PATH.glob("T12*.*"):
        if f.suffix in ['.csv', '.xlsx', '.xls']: process_t12(f)
