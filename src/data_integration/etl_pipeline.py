#!/usr/bin/env python3
"""
Clinical Data Management ETL Pipeline
Processes MIMIC-III demo data for clinical trial simulation
"""

import pandas as pd
import numpy as np
import sqlite3
import logging
from datetime import datetime, timedelta
from pathlib import Path

class ClinicalDataETL:
    def __init__(self):
        self.setup_logging()
        self.db_path = 'data/clinical_data.db'
        self.mimic_path = Path('data/raw')
        
    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        
    def load_mimic_data(self):
        """Load key MIMIC-III tables"""
        self.logger.info("Loading MIMIC-III data...")
        
        tables = {}
        key_files = ['PATIENTS.csv', 'ADMISSIONS.csv', 'LABEVENTS.csv', 'PRESCRIPTIONS.csv']
        
        for file in key_files:
            file_path = self.mimic_path / file
            if file_path.exists():
                table_name = file.replace('.csv', '').lower()
                tables[table_name] = pd.read_csv(file_path)
                self.logger.info(f"Loaded {table_name}: {len(tables[table_name])} records")
        
        return tables
    
    def create_clinical_trial_data(self, mimic_data):
        """Transform MIMIC data into clinical trial format"""
        patients = mimic_data['patients'].copy()
        admissions = mimic_data['admissions'].copy()
        
        # Create demographics using correct column names
        demographics = patients.merge(admissions, on='subject_id', how='inner')
        demographics = demographics.groupby('subject_id').first().reset_index()
        
        # Clean and transform
        # Calculate age from DOB (note: MIMIC dates are shifted to future for privacy)
        demographics['dob'] = pd.to_datetime(demographics['dob'])
        demographics['age'] = np.abs(2023 - demographics['dob'].dt.year)
        
        # Handle the shifted ages (MIMIC shifts very old patients to 300+ years)
        demographics['age'] = demographics['age'].clip(18, 90)
        
        demographics['enrollment_date'] = pd.to_datetime('2023-01-01') + pd.to_timedelta(
            np.random.randint(0, 365, len(demographics)), unit='D'
        )
        demographics['site_id'] = np.random.randint(1, 6, len(demographics))
        demographics['treatment_arm'] = np.random.choice(['Active', 'Control'], len(demographics))
        
        # Create adverse events from this patient population
        adverse_events = []
        ae_terms = ['Nausea', 'Fatigue', 'Diarrhea', 'Headache', 'Rash', 'Dizziness', 'Vomiting', 'Constipation']
        
        for _, patient in demographics.iterrows():
            n_aes = np.random.poisson(2)
            for _ in range(n_aes):
                adverse_events.append({
                    'subject_id': patient['subject_id'],
                    'ae_term': np.random.choice(ae_terms),
                    'severity': np.random.choice(['Mild', 'Moderate', 'Severe'], p=[0.6, 0.3, 0.1]),
                    'onset_date': patient['enrollment_date'] + timedelta(days=np.random.randint(1, 180)),
                    'related_to_study_drug': np.random.choice(['Yes', 'No', 'Possibly'], p=[0.3, 0.5, 0.2])
                })
        
        # Return cleaned datasets
        final_demographics = demographics[['subject_id', 'age', 'gender', 'enrollment_date', 'site_id', 'treatment_arm']].copy()
        
        return {
            'demographics': final_demographics,
            'adverse_events': pd.DataFrame(adverse_events)
        }
    
    def save_to_database(self, data):
        """Save processed data to SQLite database"""
        self.logger.info("Saving data to database...")
        
        with sqlite3.connect(self.db_path) as conn:
            for table_name, df in data.items():
                df.to_sql(table_name, conn, if_exists='replace', index=False)
                self.logger.info(f"Saved {table_name}: {len(df)} records")
    
    def run_pipeline(self):
        """Execute the complete ETL pipeline"""
        self.logger.info("Starting Clinical Data ETL Pipeline...")
        
        # Load MIMIC data
        mimic_data = self.load_mimic_data()
        
        # Transform to clinical trial format
        clinical_data = self.create_clinical_trial_data(mimic_data)
        
        # Save to database
        self.save_to_database(clinical_data)
        
        self.logger.info("ETL Pipeline completed successfully!")
        print("✅ Clinical Data ETL completed!")
        print(f"📊 Demographics: {len(clinical_data['demographics'])} subjects")
        print(f"⚠️  Adverse Events: {len(clinical_data['adverse_events'])} events")
        print(f"💾 Database saved to: {self.db_path}")

if __name__ == "__main__":
    etl = ClinicalDataETL()
    etl.run_pipeline()
