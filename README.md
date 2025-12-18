# Axim_T12_Extractor
Automated T12 Layer-1 Financial Extractor: A structural financial modeling engine that programmatically deconstructs unstructured Trailing-12 statements. Unlike keyword-based parsers, this uses a Summation Trail Audit to mathematically prove the relationship between granular accounts (Layer 1) and synthetic totals (Layers 2-4).

## 📌 Project Overview
In real estate underwriting, **Trailing-12 (T12)** financial statements are exported from dozens of different accounting platforms (Yardi, AppFolio, RealPage), each with inconsistent layouts and nested hierarchies.

This engine provides a **Format-Agnostic** solution to extract only **Layer 1 (Granular Account)** data. It ignores subtotals, category headers, and NOI lines by mathematically auditing the relationships between rows, ensuring that only the "source" data is captured for analysis.

# AXiM T12 Extraction Engine
https://axim-t12-extractor.streamlit.app/


## 🚀 Key Features

* **Grid Density Detection:** Automatically locates the 12-month numeric block regardless of where it starts on the spreadsheet, eliminating the need for hard-coded column indices.
* **Summation Trail Logic:** Unlike fragile keyword-based parsers, a row is excluded only if the engine mathematically proves it is a subtotal of a contiguous block of "active" rows above it.
* **NOI Subtraction Proofing:** Specifically identifies "Net Operating Income" and "Cash Flow" lines by detecting the mathematical difference between preceding income and expense blocks.
* **Spatial Labeling:** A heuristic-based label capture system that identifies account names across shifting column indentations and merged cells.
* **Audit Trail:** Every exported row includes a `Status` column, providing full transparency by explaining the mathematical reason for its inclusion (Granular Item) or exclusion (Subtotal/NOI).

## 🛠️ Tech Stack

* **Python 3.10+**
* **Pandas & NumPy:** Leveraged for high-speed matrix manipulation and data cleaning.
* **Pathlib:** Utilized for robust, cross-platform directory and file handling.
* **Streamlit (Optional):** Integrated support for a front-end drag-and-drop UI.

## 📂 Repository Structure

```text
/AXiM_T12_Project
│── notebooks/
│   └── T12_Extractor.ipynb   # Interactive breakdown of the algorithm
│── src/
│   └── main.py               # Production-ready extraction script
│   └── app.py                # Production-ready streamlit app script
│── data/
│   ├── input/                # Place raw T12 exports (XLSX/CSV) here
│   └── output/               # Processed Layer 1 CSVs with Audit Trails
│── requirements.txt          # Python dependencies
└── README.md                 # Project documentation
