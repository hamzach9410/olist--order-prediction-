"""
Step 1: Download Olist dataset from Kaggle.
Run: python download_data.py
Requires: pip install kaggle  +  ~/.kaggle/kaggle.json API key
OR manually download from https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce
and place CSVs inside ./data/
"""
import os

dataset = "olistbr/brazilian-ecommerce"
out_dir = "./data"

os.makedirs(out_dir, exist_ok=True)
os.system(f"kaggle datasets download -d {dataset} -p {out_dir} --unzip")
print("Done. Check ./data/")
