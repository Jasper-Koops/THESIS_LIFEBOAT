from bs4 import BeautifulSoup
from datetime import datetime
import re
import requests
import sqlite3
import time
import wget
import os


#Automate your thesis (because you will fail if you wont)
#Jasper Koops, 2017

def save_to_db(result_title, title, excerpt, article_type, no_pages, document_link, fetched_on):
    #Saves the data to the database
    data = sqlite3.connect("scraper_save_file.db")
    c = data.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS saved_data
    (result_title TEXT, title TEXT, excerpt TEXT, article_type TEXT, no_pages INT, document_link TEXT, fetched_on TEXT)''')

    now = datetime.now()

    c.execute("""
            INSERT INTO saved_data
            (result_title, title, excerpt, article_type, no_pages, document_link, fetched_on) VALUES
            (?,?,?,?,?,?,?)""", (result_title, title, excerpt, article_type, no_pages, document_link, fetched_on))
    data.commit()


def downloader(url):
    url = url
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'lxml')
    container = soup.find('div', {'class': ['left']})
    pdf_files = container.select('.download')
    html_files = container.select('.html')

    #wget.download(url)



#Ik heb de 'a' binnen div Nodig
#pre download link
#pdf download link
#text download link


def scraper(url):
    """Scrapes the webpage"""

    for x in range(0,1):
        url = url

        while True:

            time.sleep(1) #Crash voorkomen

            res = requests.get(url)
            soup = BeautifulSoup(res.text, 'lxml')

            container = soup.find('ul', {'class':['arrow', 'searchres', 'left']})
            # items = container.find_all('strong')
            items = container.find_all('li')

            for item in items:
                #find and store the main result title to variable
                result_title = item.find('strong').text
                #find and store the optional title to variable
                title = item.select('.title')
                for text in title:
                    title = text.text
                    if len(title) < 1:
                        title = "NO TITLE"
                #find and store the excerpt text to variable
                excerpt = item.find('span',{'class': None}).text
                #find and store the article type to variable
                if result_title.startswith('Handelingen Eerste Kamer') or result_title.startswith('Handelingen Tweede Kamer'):
                    article_type = 'Kamerverslag'
                elif result_title.startswith('Kamerstuk'):
                    article_type = 'Kamerstuk'
                elif result_title.startswith('Aanhangsel'):
                    article_type = 'Kamervraag'
                else:
                    article_type = 'UNKNOWN'
                #find and store the number of pages text to variable
                no_pages = item.find('div',{'class':"widget"}).text
                no_pages = re.findall("\d+", no_pages)
                #   - Geeft een lijst (met 1 element) als resultaat, maak er een int van
                for list_item in no_pages:
                    no_pages = int(list_item)
                #find and store the link to the document to a variable
                document_link = item.find('a')
                document_link = document_link.attrs['href']
                document_link = "http://www.statengeneraaldigitaal.nl" + document_link
                #find and store the fetched on date and time to the variable
                now = datetime.now()
                fetched_on = "%02d-%02d-%d %02d:%02d:%02d" % (now.day, now.month, now.year, now.hour, now.minute, now.second)

                save_to_db(result_title, title, excerpt, article_type, no_pages, document_link, fetched_on)


            pre_page_url = soup.findAll("a", title="Volgende pagina")
            for x in pre_page_url:
                try:

                    next_page_url = x.attrs['href']
                    next_page_url = "http://www.statengeneraaldigitaal.nl" + next_page_url

                except:
                    print("Ending program")2
                    exit()

            if len(next_page_url) == 0:
                print("Ending program")
                break
            else:
                url = next_page_url
                print(url)
                print("Proceeding to next page")


url = "http://www.statengeneraaldigitaal.nl/uitgebreidzoeken/zoekresultaten?vergaderjaar%5Bvan%5D=1814+-+1815&vergaderjaar%5Btot%5D=1950+-+1951&zoekwoorden=migratie&kamer%5B0%5D=Eerste+Kamer&kamer%5B1%5D=Tweede+Kamer&kamer%5B2%5D=Verenigde+Vergadering&kamer%5B3%5D=UCV%2FOCV&documentType=Alle+document+types&sortering=datum%28oplopend%29&pagina=1"


scraper(url)
