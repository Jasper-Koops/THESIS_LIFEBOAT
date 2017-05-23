import sqlite3

data = sqlite3.connect("scraper_save_file.db")
c = data.cursor()
c.execute("ALTER TABLE saved_data ADD COLUMN 'document_text' TEXT")
c.execute("ALTER TABLE saved_data ADD COLUMN 'pdf_url' TEXT")
c.execute("ALTER TABLE saved_data ADD COLUMN 'enhanced_on' TEXT")

#df = pd.read_sql_query("SELECT * FROM saved_data", data)
