from bs4 import BeautifulSoup
from datetime import datetime
import re
import requests
import sqlite3
import time
import wget
import os
import PyPDF2
import os
import random

#Save functie nodig (TENZIJ JE DE SCRAPER INVOEGT)
#Programma crashed als de database niet aanwezig is (want de savefunctie wordt niet ingeladen)


def reader(title):
    """Leest de PDF en converteert het naar TEXT"""
    pdfFileObj = open(title,'rb')
    pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
    text = ""
    maxpage = int(pdfReader.numPages) + 1
    for x in range(0, maxpage + 100):
        try:
            pageObj = pdfReader.getPage(x)
            text += str(pageObj.extractText())
        except:
            break
    return text


def pdf_link_fixer(url):
    """Fixed de directe url naar het pdf bestand, kan niet via downloader want die doet kut"""
    url = url
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'lxml')
    #Get link to PDF file
    pdf_link = soup.find('a', {'class': ['download']})
    pdf_link = pdf_link.attrs['href']
    #Get link to HTML file
    html_link = soup.find('a', {'class': ['html']})
    html_link = html_link.attrs['href']
    #Download the file
    return pdf_link


def downloader(url, alto_title):
    """Downloads the actual documents"""
    url = url
    res = requests.get(url)
    soup = BeautifulSoup(res.text, 'lxml')
    #Get link to PDF file
    pdf_link = soup.find('a', {'class': ['download']})
    pdf_link = pdf_link.attrs['href']
    #Get link to HTML file
    html_link = soup.find('a', {'class': ['html']})
    html_link = html_link.attrs['href']
    #Download the file
    # response = requests.get(pdf_link)
    # with open(filename + '.pdf', 'wb') as f:
    #     f.write(response.content)
    # f.close()

    #Programma crashed als de filename te lang is, dit is de beveiliging hiertegen
    #filename = str(alto_title)
    wget.download(pdf_link, alto_title)

    # try:
    #     wget.download(pdf_link, filename)
    # except:
    #     print("ERROR")
    #     print("pdf_link = %s\nfilename = %s\nLenght of Filename = %d" % (pdf_link, filename, len(filename)))
    # # except:
    #     print("Filename to long, intervening...")
    #     filename = filename[0:120]
    #     wget.download(pdf_link, filename)


def save_to_db(result_title, title, excerpt, article_type, no_pages, document_link, fetched_on, document_text, pdf_url, enhanced_on):
    """Saves the data to the database"""
    data = sqlite3.connect("scraper_save_file.db")
    c = data.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS saved_data
    (result_title TEXT, title TEXT, excerpt TEXT, article_type TEXT, no_pages INT, document_link TEXT, fetched_on, document_text TEXT, pdf_url TEXT, enhanced_on TEXT)''')

    now = datetime.now()

    c.execute("""
            INSERT INTO saved_data
            (result_title, title, excerpt, article_type, no_pages, document_link, fetched_on, document_text, pdf_url, enhanced_on) VALUES
            (?,?,?,?,?,?,?,?,?,?)""", (result_title, title, excerpt, article_type, no_pages, document_link, fetched_on, document_text, pdf_url, enhanced_on))
    data.commit()


#load data into a pandas DataFrame.
data = sqlite3.connect("scraper_save_file.db")
c = data.cursor()

#This part scans the database for empty fields and appends them. Requires internet as there is some downloading involved
while True:

    #Pause program to avoid detection
    pause_length = random.randint(30,90)
    print("pausing for %d seconds to avoid detection" % (pause_length))
    time.sleep(pause_length)

    c.execute('SELECT result_title, title, document_link FROM saved_data WHERE pdf_url is null')
    info = c.fetchone()
    result_title = info[0]
    title = info[1]
    document_link = info[2]

    #Download files and read contents


    if title == 'NO TITLE':
        alto_title = str(result_title)
        if len(alto_title) > 120:
            print("Filename too long, intervening...")
            alto_title = alto_title[0:110]
        #Als bestandsnaam al bestaat moet je hem aanpassen, anders crashed ie
        while os.path.isfile(alto_title) == True:
            alto_title = alto_title + str(random.randint(1,9999))
        downloader(document_link, alto_title)
        downloaded_text = reader(alto_title)

    else:
        alto_title = str(result_title)
        if len(alto_title) > 120:
            print("Filename too long, intervening...")
            alto_title = alto_title[0:110]
        #Als bestandsnaam al bestaat moet je hem aanpassen, anders crashed ie
        while os.path.isfile(alto_title) == True:
            alto_title = alto_title + str(random.randint(1,9999))
        downloader(document_link, alto_title)
        downloaded_text = reader(alto_title)




    #Update row by appending document_text, pdf_link and enchanced_on date
    now = datetime.now()
    enhanced_on = "%02d-%02d-%d %02d:%02d:%02d" % (now.day, now.month, now.year, now.hour, now.minute, now.second)
    pdf_url = pdf_link_fixer(document_link)

    c.execute('UPDATE saved_data SET document_text=? WHERE result_title = ?', (downloaded_text,result_title,))
    c.execute('UPDATE saved_data SET pdf_url=? WHERE result_title = ?', (pdf_url,result_title,))
    c.execute('UPDATE saved_data SET enhanced_on=? WHERE result_title = ?', (enhanced_on, result_title,))

    print(title)
    data.commit()
