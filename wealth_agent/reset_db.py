import sqlite3
conn = sqlite3.connect('C:/Users/jeanl/OneDrive/Desktop/JM_project_nxstep/nxstep_site/wealth_agent/data/leads_database.db')
cursor = conn.cursor()
cursor.execute("UPDATE leads SET status='Scrapé', icebreaker=NULL")
conn.commit()
conn.close()
print("Base de donnée réinitialisée.")
