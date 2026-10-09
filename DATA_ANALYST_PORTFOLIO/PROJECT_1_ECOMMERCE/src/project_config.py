"""
RETAILEDGE - Central project configuration
==========================================
All scripts resolve data/report paths from this module so the project is
portable and does not depend on any machine-specific absolute path.
"""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

RAW_DATA_PATH = PROJECT_ROOT / 'data' / 'raw'
PROCESSED_DATA_PATH = PROJECT_ROOT / 'data' / 'processed'
POWERBI_DATA_PATH = PROJECT_ROOT / 'data' / 'powerbi'
EXCEL_PATH = PROJECT_ROOT / 'excel'
FIGURES_PATH = PROJECT_ROOT / 'reports' / 'figures'
BUSINESS_ANALYSIS_PATH = PROJECT_ROOT / 'reports' / 'business_analysis'

for _dir in [RAW_DATA_PATH, PROCESSED_DATA_PATH, POWERBI_DATA_PATH,
             EXCEL_PATH, FIGURES_PATH, BUSINESS_ANALYSIS_PATH]:
    _dir.mkdir(parents=True, exist_ok=True)