import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import io

# --- REUSE YOUR EXACT CLEANING LOGIC ---
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
    return max(text_cells, key=len) if text_cells else ""

# --- DASHBOARD UI ---
st.set_page_config(page_title="AXiM T12 Extractor", layout="wide")
st.title("📊 AXiM Layer-1 Financial Extractor")
st.markdown("Upload a T12 (Excel or CSV) to extract granular Layer-1 data and generate a mathematical audit trail.")

uploaded_file = st.file_uploader("Choose a T12 file", type=['csv', 'xlsx', 'xls'])

if uploaded_file:
    # Read the file
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file, header=None).fillna('')
    else:
        df = pd.read_excel(uploaded_file, header=None).fillna('')

    # 1. GRID DETECTION
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
    audit_trail = ["Layer 1 Item"] * len(df)

    # 2. SUMMATION TRAIL
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

    # 3. EXTRACTION
    extracted = []
    for i in range(len(df)):
        label = get_best_label(df.iloc[i].values, best_start)
        if not is_total[i] and label:
            row_dict = {"Account": label, "Status": audit_trail[i]}
            for m in range(12):
                row_dict[f"Month_{m+1}"] = data_grid[i, m]
            row_dict["Total"] = row_sums[i]
            extracted.append(row_dict)

    if extracted:
        res_df = pd.DataFrame(extracted)
        st.success(f"Successfully extracted {len(res_df)} Layer-1 line items!")
        
        # Display Audit View
        st.subheader("Data Preview & Audit Trail")
        st.dataframe(res_df, use_container_width=True)
        
        # Download Button
        csv = res_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Download Processed Layer-1 CSV",
            data=csv,
            file_name=f"L1_{uploaded_file.name.split('.')[0]}.csv",
            mime='text/csv',
        )
