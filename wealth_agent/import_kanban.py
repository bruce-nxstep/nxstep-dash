import pandas as pd
import sys
import os

# Ensure the src folder is accessible
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))
from database import DatabaseManager

def import_google_sheet(db_path='data/leads_database.db', url='https://docs.google.com/spreadsheets/d/1IaoKzVIHR3d-YFJVKdqjxT-ks18QdyM-P_bDPhV98Yg/export?format=csv'):
    print(f"Downloading data from: {url}")
    try:
        # Load the CSV
        df = pd.read_csv(url)
        print(f"Loaded {len(df)} rows.")
        
        # Initialize DB
        db = DatabaseManager(db_path)
        
        # Count imports
        imported_count = 0
        
        for index, row in df.iterrows():
            # Standardize names to match what we saw in the printout
            departement = str(row.get('Département', '')).strip()
            title = str(row.get('Fonction / Cas d\'usage principal', '')).strip()
            needs = str(row.get('Besoins', '')).strip()
            solutions = str(row.get('Solutions envisagées', '')).strip()
            tools = str(row.get('Outils / Logiciels', '')).strip()
            system_prompt = str(row.get('Système prompt', '')).strip()
            
            # Skip empty Titles
            if not title or title.lower() == 'nan':
                continue
                
            # Replace 'nan' string with empty string
            departement = "" if departement.lower() == 'nan' else departement
            needs = "" if needs.lower() == 'nan' else needs
            solutions = "" if solutions.lower() == 'nan' else solutions
            tools = "" if tools.lower() == 'nan' else tools
            system_prompt = "" if system_prompt.lower() == 'nan' else system_prompt
            
            db.add_task(
                departement=departement,
                title=title,
                needs=needs,
                solutions=solutions,
                tools=tools,
                system_prompt=system_prompt,
                status="À faire"
            )
            imported_count += 1
            
        print(f"Success! Imported {imported_count} tasks into the SQLite database.")
        
    except Exception as e:
        print(f"Error importing data: {e}")

if __name__ == "__main__":
    import_google_sheet()
