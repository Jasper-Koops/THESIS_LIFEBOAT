import sqlite3

import sqlite3




def analysed_save_to_db(result_title, title, excerpt, article_type, no_pages, document_link, fetched_on, document_text, pdf_url, enhanced_on, abstracts, article_rank, number_of_mentions, NORMALIZED_number_of_mentions, date_of_analysis, used_search_terms, estimated_publication_date, row_id):
    """Saves the data to the database"""
    data = sqlite3.connect("django_unchained.db")
    c = data.cursor()

    c.execute('''
    CREATE TABLE IF NOT EXISTS saved_data
    (result_title TEXT, title TEXT, excerpt TEXT, article_type TEXT, no_pages INT, document_link TEXT, fetched_on, document_text TEXT, pdf_url TEXT, enhanced_on TEXT, abstracts TEXT, article_rank INT, number_of_mentions INT, NORMALIZED_number_of_mentions REAL, date_of_analysis TEXT, used_search_terms TEXT, estimated_publication_date INT, row_id INT)''')




    c.execute("""
            INSERT INTO saved_data
            (result_title, title, excerpt, article_type, no_pages, document_link, fetched_on, document_text, pdf_url, enhanced_on, abstracts, article_rank, number_of_mentions, NORMALIZED_number_of_mentions, date_of_analysis, used_search_terms, estimated_publication_date, row_id) VALUES
            (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?, ?)""", (result_title, title, excerpt, article_type, no_pages, document_link, fetched_on, document_text, pdf_url, enhanced_on, abstracts, article_rank, number_of_mentions, NORMALIZED_number_of_mentions, date_of_analysis, used_search_terms,estimated_publication_date, row_id))
    data.commit()


def number_generator():
    data = sqlite3.connect("analysed.db")
    c = data.cursor()
    # data = sqlite3.connect("analysed.db", timeout=3)
    # c = data.cursor()
    number = 0

    print("Column already present, generating numbers...")
    info = c.execute('SELECT result_title, title, excerpt, article_type, no_pages, document_link, fetched_on, document_text, pdf_url, enhanced_on, abstracts, article_rank, number_of_mentions, NORMALIZED_number_of_mentions, date_of_analysis, used_search_terms, estimated_publication_date, row_id from saved_data')
    rows = info.fetchall()
    for row in rows:


        result_title = str(row[0])
        title = str(row[1])
        excerpt = str(row[2])
        article_type = str(row[3])
        no_pages = row[4]
        document_link = row[5]
        fetched_on = row[6]
        document_text = row[7]
        pdf_url = row[8]
        enhanced_on = row[9]
        abstracts = row[10]
        article_rank = row[11]
        number_of_mentions = row[12]
        NORMALIZED_number_of_mentions = row[13]
        date_of_analysis = row[14]
        used_search_terms = row[15]
        estimated_publication_date = row[16]
        row_id = number

        number += 1
        print(row_id)

        analysed_save_to_db(result_title, title, excerpt, article_type, no_pages, document_link, fetched_on, document_text, pdf_url, enhanced_on, abstracts, article_rank, number_of_mentions, NORMALIZED_number_of_mentions, date_of_analysis, used_search_terms, estimated_publication_date, row_id)







try:
    c.execute("ALTER TABLE saved_data ADD COLUMN 'row_id' INTEGER")
    print("Column created, run again to generate numbers")
except:
    print("is er al")
    number_generator()
