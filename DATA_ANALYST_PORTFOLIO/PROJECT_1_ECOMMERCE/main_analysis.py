"""
RETAILEDGE - Main Analysis Pipeline
====================================
This is the main script that runs the complete analysis pipeline.
"""

import sys
import os

# Add src folder to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from data_cleaning import DataCleaner
from data_validation import DataValidator
from feature_engineering import FeatureEngineer
from notebooks.eda_analysis import EDAAnalyzer
from project_config import RAW_DATA_PATH, PROCESSED_DATA_PATH, FIGURES_PATH

def main():
    """Run complete analysis pipeline"""
    
    print("="*70)
    print("RETAILEDGE - E-COMMERCE REVENUE, CUSTOMER & FINANCIAL ANALYTICS")
    print("="*70)
    
    # Paths
    raw_data_path = RAW_DATA_PATH
    processed_data_path = PROCESSED_DATA_PATH
    output_path = FIGURES_PATH
    
    # Step 1: Data Cleaning
    print("\n" + "="*70)
    print("STEP 1: DATA CLEANING")
    print("="*70)
    cleaner = DataCleaner(raw_data_path)
    cleaner.clean_all()
    
    # Step 2: Data Validation
    print("\n" + "="*70)
    print("STEP 2: DATA VALIDATION")
    print("="*70)
    validator = DataValidator(processed_data_path)
    validator.run_all_validations()
    
    # Step 3: Feature Engineering
    print("\n" + "="*70)
    print("STEP 3: FEATURE ENGINEERING")
    print("="*70)
    engineer = FeatureEngineer(processed_data_path)
    engineer.engineer_all()
    
    # Step 4: Exploratory Data Analysis
    print("\n" + "="*70)
    print("STEP 4: EXPLORATORY DATA ANALYSIS")
    print("="*70)
    eda = EDAAnalyzer(processed_data_path, output_path)
    eda.run_full_eda()
    
    # Final Summary
    print("\n" + "="*70)
    print("ANALYSIS PIPELINE COMPLETE!")
    print("="*70)
    print("\nFiles created:")
    print("  • data/processed/ - Cleaned data files")
    print("  • data/processed/ - Engineered features")
    print("  • reports/figures/ - EDA visualizations")
    print("\nNext steps:")
    print("  • Review visualizations in reports/figures/")
    print("  • Run SQL queries for business analysis")
    print("  • Build Power BI dashboard")
    print("="*70)


if __name__ == "__main__":
    main()
