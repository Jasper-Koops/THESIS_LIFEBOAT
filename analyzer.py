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

#See variables at the bottom for further information.





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

    try:
        estimated_publication_date = int(re.findall('19\d\d|18\d\d', string)[-1])
        if estimated_publication_date > 1960:
            estimated_publication_date = None
    except:
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

            analysed_save_to_db(result_title, title, excerpt, article_type, no_pages, document_link, fetched_on, document_text, pdf_url, enhanced_on, abstracts, article_rank, number_of_mentions, NORMALIZED_number_of_mentions, date_of_analysis, used_search_terms, estimated_publication_date)

        except:
            print("Row analysis failed for some reasons, skipping...")





















#The keywords that you wish to search for. Consider using partial words to include spelling / scanning mistakes (EG 'migr' instead of 'migrants')
keywords = []
#How many words you wish to include on each side
search_range = 80
#To avoid duplicate paragraphs the program filters out paragrahps that are deemed to be to similar to those that are already included.\nInput the percentage point (e.g: '90' for 90%) of how much overlap paragrahps are alowed to have before they are removed by the program\nA score of 90 is recommended
accuracy = 90
iterator(keywords, search_range, accuracy)
