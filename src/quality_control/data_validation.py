#!/usr/bin/env python3
"""
Clinical Data Quality Control and Validation System
"""

import pandas as pd
import numpy as np
import sqlite3
import logging
from datetime import datetime

class ClinicalDataValidator:
    def __init__(self, db_path='data/clinical_data.db'):
        self.db_path = db_path
        self.validation_results = []
        self.setup_logging()
        
    def setup_logging(self):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def load_data(self, table_name):
        with sqlite3.connect(self.db_path) as conn:
            return pd.read_sql(f"SELECT * FROM {table_name}", conn)
    
    def validate_demographics(self):
        self.logger.info("Validating demographics data")
        df = self.load_data('demographics')
        
        # Age validation
        age_violations = df[(df['age'] < 18) | (df['age'] > 120)]
        if not age_violations.empty:
            self.validation_results.append({
                'table': 'demographics',
                'rule': 'age_range',
                'violations': len(age_violations),
                'severity': 'Error',
                'message': f'{len(age_violations)} subjects with invalid age'
            })
    
    def run_all_validations(self):
        self.logger.info("Starting data validation")
        self.validate_demographics()
        
        if not self.validation_results:
            print("✅ All data quality checks passed!")
        else:
            print("Data Quality Issues Found:")
            for issue in self.validation_results:
                print(f"- {issue['severity']}: {issue['message']}")

if __name__ == "__main__":
    validator = ClinicalDataValidator()
    validator.run_all_validations()
