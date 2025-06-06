#!/usr/bin/env python3
"""
CDISC SDTM Data Mapping System
"""

import pandas as pd
import sqlite3
import logging

class CDISCSDTMMapper:
    def __init__(self, db_path='data/clinical_data.db'):
        self.db_path = db_path
        self.setup_logging()
        
    def setup_logging(self):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
    
    def load_source_data(self, table_name):
        with sqlite3.connect(self.db_path) as conn:
            return pd.read_sql(f"SELECT * FROM {table_name}", conn)
    
    def map_demographics_dm(self):
        self.logger.info("Mapping Demographics to CDISC DM domain")
        
        source_dm = self.load_source_data('demographics')
        dm = pd.DataFrame()
        
        # CDISC SDTM DM domain mapping
        dm['STUDYID'] = 'DEMO-001'
        dm['DOMAIN'] = 'DM'
        dm['USUBJID'] = 'DEMO-001-' + source_dm['subject_id'].astype(str).str.zfill(4)
        dm['SUBJID'] = source_dm['subject_id'].astype(str)
        dm['RFSTDTC'] = pd.to_datetime(source_dm['enrollment_date']).dt.strftime('%Y-%m-%d')
        dm['AGE'] = source_dm['age']
        dm['AGEU'] = 'YEARS'
        dm['SEX'] = source_dm['gender']
        dm['ARM'] = source_dm['treatment_arm']
        
        return dm
    
    def export_sdtm_domains(self):
        self.logger.info("Exporting SDTM domains")
        
        dm = self.map_demographics_dm()
        
        # Create output directory
        import os
        os.makedirs('output/sdtm', exist_ok=True)
        
        # Export DM domain
        dm.to_csv('output/sdtm/dm.csv', index=False)
        
        print("✅ CDISC SDTM Export Complete:")
        print(f"  DM Domain: {len(dm)} records")
        
        return dm

if __name__ == "__main__":
    mapper = CDISCSDTMMapper()
    mapper.export_sdtm_domains()
