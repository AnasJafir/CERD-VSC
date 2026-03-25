import openpyxl
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent
DATA_DIR = ROOT_DIR / "data"
EXCEL_PATH = DATA_DIR / "Tables B3D_V1_Excel-3.3.26 Corrigé.xlsx"

print(f"Reading headers from: {EXCEL_PATH}")
wb = openpyxl.load_workbook(EXCEL_PATH, read_only=True)
ws = wb['Feuil1']
headers = [c.value for c in next(ws.rows)]
print("Headers:", headers)
