from bs4 import BeautifulSoup
from datetime import datetime
from fuzzywuzzy import fuzz
from collections import defaultdict
import itertools
import re
import requests
import sqlite3
import time
import wget #kan weg volgens mij
import os #Moet nog worden gebruikt
import PyPDF2
import random
import matplotlib.pyplot as plt


#TODO:
#Scan titel (1e titel, die er atlijd is) voor het LAATSTE genoemde jaartal.
#Geef het artikel dat getal als jaartal in kolom.
#creer (PER ZOEKWOORD) een datatime lijngrafiek van hoeveel hits ze in de loop der tijd krijgen
#HIervoo rmoet je een 'used search terms' ding maken als colom.
#Creeër automatisch een text bestand met de used url en search terms en andere settings
#Sta argv toe en gebruik menu alleen als de laatste er niet is <-- Heb je bij ander programma eerder gedaan.

#Database uitbreiding:
# 1. Esimated publication date (use RE to find latest date)
# 2. Search terms used

#Graphs for word occurence NORMALIZED vs NON_NORMALIZED (Or both in the same graph?)  <-- Linechart
#Graphs for which word has the most total mentions   <-- barchart
#Scatterplot / regresion for likelyhood of 1 word for the occurance of others?  <--- GEEN NUT. HOBBY


def menu():
    print("Welcome to THESIS STALINGRAD 2017\n")
    choice = int(input("What do you want to do?\n1. Index new files\n2. Download Indexed files\n3. Process for keywords\n4. Index + Fetch + Process\n5. Exit\n> "))

    if choice == 1:
        url = input("What is the url of the search result that you want to index?\n> ")
        print("starting scraper")
        scraper(url)

    if choice == 2:
        print("starting fetcher")
        fetcher()

    if choice == 3:
        #Start program
        keyword_choice = input("What keywords do you want to use in the analysis? (separate by space)\n> ")
        keywords_selection = [x for x in keyword_choice.split()]
        search_range = int(input("How many words around each keyword (once for earch side) should I incorporate in the analysis?\n> "))
        accuracy = int(input("To avoid duplicate paragraphs the program filters out paragrahps that are deemed to be to similar to those that are already included.\nInput the percentage point (e.g: '90' for 90%) of how much overlap paragrahps are alowed to have before they are removed by the program\nA score of 90 is recommended\n> "))
        print("Got it, starting analysis")
        iterator(keywords_selection, search_range, accuracy)

    if choice == 4:
        url = input("What is the url of the search result that you want to index?\n> ")
        keyword_choice = input("What keywords do you want to use in the analysis? (separate by space)\n> ")
        keywords_selection = [x for x in keyword_choice.split()]
        search_range = int(input("How many words around each keyword (once for earch side) should I incorporate in the analysis?"))
        accuracy = int(input("To avoid duplicate paragraphs the program filters out paragrahps that are deemed to be to similar to those that are already included.\nInput the percentage point (e.g: '90' for 90%) of how much overlap paragrahps are alowed to have before they are removed by the program\nA score of 90 is recommended"))
        print("Got it, starting analysis")
        print("Go to bed, get some rest. Let the computer do the rest")
        print("STARTING SCRAPER")
        scraper(url)
        print("STARTING FETCHER")
        try:
            fetcher()
        except:
            print("Fetcher is done (most likely) or crashed (possibly)  [currently a succesfull run ends with a crash]") #Fix this bug
        print("STARTING ANALYSER")
        iterator(keywords_selection, search_range, accuracy)
        print("I'M FINISHED!             (and I drank your milkshake)")

    if choice == 5:
        print("godspeed")
        exit()


##################################################################################################
##################################################################################################
########################################### HERE BE DATABASES ####################################
##################################################################################################
##################################################################################################
def save_to_db(result_title, title, excerpt, article_type, no_pages, document_link, fetched_on):
    """Saves the data to the database"""
    data = sqlite3.connect("scraper_save_file.db")
    c = data.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS saved_data
    (result_title TEXT, title TEXT, excerpt TEXT, article_type TEXT, no_pages INT, document_link TEXT, fetched_on, document_text TEXT, pdf_url TEXT, enhanced_on TEXT, abstracts TEXT, article_rank INT, number_of_mentions INT, NORMALIZED_number_of_mentions REAL, date_of_analysis TEXT, used_search_terms TEXT, estimated_publication_date INT)''')

    now = datetime.now()

    c.execute("""
            INSERT INTO saved_data
            (result_title, title, excerpt, article_type, no_pages, document_link, fetched_on) VALUES
            (?,?,?,?,?,?,?)""", (result_title, title, excerpt, article_type, no_pages, document_link, fetched_on))
    data.commit()


def analysed_save_to_db(result_title, title, excerpt, article_type, no_pages, document_link, fetched_on, document_text, pdf_url, enhanced_on, abstracts, article_rank, number_of_mentions, NORMALIZED_number_of_mentions, date_of_analysis, used_search_terms, estimated_publication_date):
    """Saves the data to the database"""
    data = sqlite3.connect("analysed.db")
    c = data.cursor()
    c.execute('''
    CREATE TABLE IF NOT EXISTS saved_data
    (result_title TEXT, title TEXT, excerpt TEXT, article_type TEXT, no_pages INT, document_link TEXT, fetched_on, document_text TEXT, pdf_url TEXT, enhanced_on TEXT, abstracts TEXT, article_rank INT, number_of_mentions INT, NORMALIZED_number_of_mentions REAL, date_of_analysis TEXT, used_search_terms TEXT, estimated_publication_date INT)''')

    now = datetime.now()

    c.execute("""
            INSERT INTO saved_data
            (result_title, title, excerpt, article_type, no_pages, document_link, fetched_on, document_text, pdf_url, enhanced_on, abstracts, article_rank, number_of_mentions, NORMALIZED_number_of_mentions, date_of_analysis, used_search_terms, estimated_publication_date) VALUES
            (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""", (result_title, title, excerpt, article_type, no_pages, document_link, fetched_on, document_text, pdf_url, enhanced_on, abstracts, article_rank, number_of_mentions, NORMALIZED_number_of_mentions, date_of_analysis, used_search_terms,estimated_publication_date))
    data.commit()


##################################################################################################
##################################################################################################
########################### HERE BE DATABASES THE PART THAT INDEXES ##############################
##################################################################################################
##################################################################################################
def scraper(url):
    """Scrapes the search-result webpage"""
    for x in range(0,1):
        url = url

        while True:
            scraper_pause_length = random.randint(5,10)
            print("pausing for %d seconds to avoid detection" % scraper_pause_length)
            time.sleep(scraper_pause_length) #Crash voorkomen
            res = requests.get(url)
            soup = BeautifulSoup(res.text, 'lxml')
            container = soup.find('ul', {'class':['arrow', 'searchres', 'left']})
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

                #assign NULL value to unused variables
                #result_title, title, excerpt, article_type, no_pages, document_link, fetched_on, document_text, pdf_url, enhanced_on, abstracts, article_rank, number_of_mentions, NORMALIZED_number_of_mentions, date_of_analysis, used_search_terms = (None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, None)

                #save everything to the database
                save_to_db(result_title, title, excerpt, article_type, no_pages, document_link, fetched_on)


            #Proceed to the next page once all of the pages have been scanned
            pre_page_url = soup.findAll("a", title="Volgende pagina")
            for x in pre_page_url:
                try:
                    next_page_url = x.attrs['href']
                    next_page_url = "http://www.statengeneraaldigitaal.nl" + next_page_url
                except:
                    print("Ending program")
                    return

            if len(next_page_url) == 0:
                print("Ending program")
                break
            else:
                url = next_page_url
                print(url)
                print("Proceeding to next page")


##################################################################################################
##################################################################################################
########################### HERE BE DATABASES THE PART THAT FETCHES ##############################
##################################################################################################
##################################################################################################
def fetcher():
    """Parses through the database, downloads the relevant files, scans the text of their contents and saves everything to the database"""

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
        try:
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

        except:
            #Zodat ie niet stopt als een file kut doet
            pdf_url = "00000 ERROR  ERROR  ERROR  ERROR ERROR"
            c.execute('UPDATE saved_data SET pdf_url=? WHERE result_title = ?', (pdf_url,result_title,))

        print(title)
        data.commit()


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
    #ALTO DOWNLOAD MANIER
    # open in binary mode
    print(pdf_link)
    print(alto_title)
    with open(alto_title, "wb") as file:
        # get request
        print("Downloading...")
        response = requests.get(pdf_link)
        # write to file
        file.write(response.content)


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


##################################################################################################
##################################################################################################
########################### HERE BE DATABASES THE PART THAT PROCESSES ############################
##################################################################################################
##################################################################################################
def search_term_finder(keywords):
    """Turn the list of keywords into a string to be saved to the database"""
    keyword_string = ""
    for key in keywords:
        keyword_string += key + " "
    return keyword_string


def keyword_graph_maker(key, years):
    """Creates a linegraph for the occurance of the keyword"""

    # SELECT MIN(estimated_publication_date) FROM saved_data;
    # SELECT MAX(estimated_publication_date) FROM saved_data;
    #AAN HET EINDE VAN HET PROGRAMMA DE BALANS OPMAKEN
    #fetch keyword
    #fetch min jaartaal
    #fetch max jaartaal
    #loop over min tot max (stappen van 1 jaar )
        #selecteer entry die dat jaartal heeft en selecteer hits
        #Maak graph met keyword als titel
        #Save en done

        #Doe het zelfde waar je hits door pagenumbers deelt (gebruik normalized niet, die zijn voor totalen )
    pass

def publication_date_determiner(string):
    """Scans the document title for the last valid date and assumes that as the publication date"""

    estimated_publication_date = int(re.findall('19\d\d|18\d\d', string)[-1])
    if estimated_publication_date > 1960:
        estimated_publication_date = None

    return estimated_publication_date


def analyser(text, RANGE, keywords, accuracy):
    """Reads a text and returns relevant parts"""
    #IS EEN GOEDE KANS DAT HIJ NIET MEER WERKT ALS ER GEEN NULL VALUES MEER ZIJN, HERCHECK M DAN!
    #################################
    #Load text to variable
    document_text = text
    #I need these variables
    REMOVED = 0
    results = ""
    final_results = ""
    hits = 0
    index_lijst = []
    first_catch_of_today = []
    split_text = document_text.split()
    #zoek binnen lijst naar match
    for word in split_text:
        if keywords in word:
            hits += 1
            #vind index van matches en voeg aan index lijst toe
            index_lijst.append(split_text.index(word))
    #Create list of index ranges
    for index in index_lijst:
        first_catch_of_today.append((split_text[index - RANGE: index + RANGE]))
    #remove duplicates
    for this, that in itertools.combinations(first_catch_of_today, 2):
        this_match = " ".join(this)
        that_match = " ".join(that)

        rat = (fuzz.ratio(this_match,that_match))
        if rat > accuracy:
            #DEZE TRY EXCEPT LOOP MAAKT DAT HET PROGRAMMA WERKT
            #MAAR DE BUG VERTRAAGT HET PROGRAMMA ECHT ENORM.
            try:
                #first_catch_of_today.remove(that)
                first_catch_of_today.remove(this)
                print("Too simular, removing...")
                REMOVED +=1
            except:
                print("program tries to remove non-existing element, skipping...")

    #Turn these index ranges into sentences again.
    for x in first_catch_of_today:
        #echt chaos, alles dubbelop MAAR HET WERKT
        #Maakt caps van matches want dat leest fijner
        results = " ".join(x)
        results = results.split()
        for word in results:
            if keywords in word:
                index = results.index(word)
                results[index] = word.upper()
        #Create some whitespace between portions
        results.append("\n\n")
        #join them together in a return variable
        results = " ". join(results)
        final_results += results
        final_results += "\n\n"
        #hits = len(index_lijst)
    return final_results, hits


def iterator(keywords, search_range, accuracy):
    """Iterates over the rows within the database and peforms operations on them"""
    hitdict = {}
    dictlist = []

    data = sqlite3.connect("scraper_save_file.db")
    c = data.cursor()
    total_hits = 0
    row_count = 1

    rows = c.execute("SELECT result_title, title, excerpt, article_type, no_pages, document_link, fetched_on, document_text, pdf_url, enhanced_on, abstracts, article_rank, number_of_mentions, NORMALIZED_number_of_mentions, date_of_analysis, used_search_terms estimated_publication_date FROM saved_data")

    for row in rows:
        print("Summarizing row: %d" % row_count)
        row_count += 1

        try:
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
            used_search_terms = search_term_finder(keywords)
            estimated_publication_date = publication_date_determiner(result_title)

            #Als ie leeg is moet ie naar nul, anders crashed het programma
            if number_of_mentions == None:
                number_of_mentions = 0
            #print(result_title)
            #
            for key in keywords:
                abstract_text, number_of_results = analyser(document_text, search_range, key, accuracy)
                number_of_mentions += number_of_results

                if abstracts == None:
                    abstracts = ""
                abstracts += abstract_text
                abstracts += "\n\n"

                #Calculate NORMALIZED_number_of_mentions
                NORMALIZED_number_of_mentions = number_of_mentions / no_pages


            #Hercalculeer hier de rank, het heeft enige peformance penalty om dat hier in te code te doen, maar g dit is veel duidelijker


            #Calculeer hier het jaartal (apparte functie)  #VOEG COLUMN TOE

            #Maak hier de graphs? Of in de functie
            #En op een database van enkele honderden documenten (en sowieso al een paar uur analyse tijd) maakt dit echt geen ene reet uit.
            print(abstracts)
            analysed_save_to_db(result_title, title, excerpt, article_type, no_pages, document_link, fetched_on, document_text, pdf_url, enhanced_on, abstracts, article_rank, number_of_mentions, NORMALIZED_number_of_mentions, date_of_analysis, used_search_terms, estimated_publication_date)

        except:
            print("Row analysis failed for some reasons, skipping...")

    #AAN HET EINDE VAN HET PROGRAMMA DE BALANS OPMAKEN

    #fetch keyword
    #fetch min jaartaal
    #fetch max jaartaal
    #loop over min tot max (stappen van 1 jaar )
        #selecteer entry die dat jaartal heeft en selecteer hits
        #Maak graph met keyword als titel
        #Save en done

        #Doe het zelfde waar je hits door pagenumbers deelt (gebruik normalized niet, die zijn voor totalen )





#RUN THE PROGRAM
menu()




#                 #maak hier de hitdict per keyword, moet hier want we moeten data hebben die straks word opgeslagen




#                 #list als value met daarin dicts van jaar en value
#
#                 #Append dictlist with list of the following values
#
#
#                 for x in hitlist:
#                     if x[0] in hitdicts:
#                         hitdict[key].append([x[1], x[2]])
#                     else:
#                         #hitdict[x[0]] = VALUE
#                         hitdict[key] = [x[1], x[2]]
#
#
#                 dictlist.append([key, estimated_publication_date, number_of_results])
#
#                 for key in keywords:
#                     for minilist in dictlist:
#                         if minilist[0] == key:
#
#
#
#
#
#
#                 #DEZE FUCNTIE CODE IS VOOR PRODUCTIE
#                 minjaar = SELECT MIN(estimated_publication_date) FROM saved_data;
#                 maxjaar = SELECT MAX(estimated_publication_date) FROM saved_data;
#
#                 for dictitem in dictlist:
#
#                     total = 0
#                     for ITERJAAR in range(minjaar, maxjaar+1)
#                         for x in value:
#                             if x[0] == ITERJAAR:
#                                 total += x[1]
#
#                         xlijst.append(ITERJAAR)
#                         ylijst.append(total)
#
#                         plt.title(key)
#                         plt.plot(xlijst, ylijst)
#                         plt.savefig(key+ ".png")
#
#
#
#
#
#
#
#
#                 hitlist.append([estimated_publication_date, number_of_results])
#
#                 from collections import defaultdict
#
# keydict = defaultdict(list)
# keydict[key].append([estimated_publication_date, number_of_results])
#
#
# for key, date in cur:
#     keydictdict[key].append(date)
#
#
#                 #IF KEY EXISTS
#                 #KEY[value] = OG_value += new_value
#
#                 hitlist.append()
#
#                 #Fetch number of results
#                 #Fetch pub+year
#                 #Combineer in dicts
#                 #append to list
#
#                 #Check is key exists
#                 if key in hitdict:
#                     #voeg toe aan de value list een dict met jaar-NUMBER_OF_RESULTS
#                     hitdict[key] = #APPEND TO LIJST MET DICTS
#
#                     yourlist.append(yourdict.copy())
#                     pass
#                 else:
#                     #create key
#                     pass
#
#
#                 #Als key nog niet bestaat:
#                     #Maak key
#                 #Als key wel bestaat
#
#
#                 # if number_of_mentions > 0:
#                 #     hitdict['key'] = int(number_of_mentions)
#                 # else:
#                 #     pass
