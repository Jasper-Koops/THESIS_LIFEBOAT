# THESIS_LIFEBOAT

# Before we get started

This program is still very much a work in progress, that is being used and developed simultaneously.
As such, the code is still of a rather poor quality with many untranslated comments and with a lot of 'hackey' solutions, to the problems that have emerged. 
Normally I would not yet open this repository to the public - but after I posted about the project on reddit I received multiple requests
to share the source code. 
I have decided to do so, but please keep in mind that the code here is in no way representative of the final version that I plan to release somewhere this fall. 
(And the code that is here will require a lot of rewriting to use it for other websites / purposes) 

# The situation 

I have to write 2 master theses and personal circumstances have caused me to lag behind on my studies
and have left me with very little time to spare. I need to start the writing process as soon as possible, yet I also have to do my research.
This entails researching the colonial archieves of the Dutch parliament from 1815 untill 1955 - which contains thousands of documents. 
The website of this arhieve is a bit of a mess, the search function does not work very well and the documents are served as scans saved as pdfs. 
A text option is avaible, but these were the result of a computer scanning the pdf's and are of a rather poor quality and full of spelling errors. 

Researching this archieve would take me months. Its like find a needle in very large and very flawed haystack.


# The solution

Enter THESIS_LIFEBOAT. This program scrapes the database website, downloads thousand of documents (taking care not to overload the servers by taking ample pauses between downloads), scans the text within these documents
(doing a lot better job at this than whatever method the archive itself used) and stores the text, title, pagenumber and other information to a database. 

The documents are then scanned and analysed for the occurence of certain keywords from my thesis, with the text surrounding each keyword being stored in a database

If these keywords are found the text surrounding these keywords is stored in a database as a 'mini-summary' and a 'number of occurances' counter is updated. The program also scans the titles of the documents to find the publication dates. 
Future versions will include graphs, to measure word occurance over time, google-ngram-style and a django based GUI to view the documents. 

This allows me to not only find the documents that are most relevant to my thesis, but also to find relevant portions of otherwise irrelevant documents. This program works, I have it run when I sleep. I have it running on 2 seperate computers for 24 hours each day and I have already analysed over 2100 documents with it (In just two days!)

# TLDR

The program downloads the files

![Alt text](/images/downloads.png?raw=true "Downloading the files...")

Then Analyzes the files

![Alt text](/images/analyzing.png?raw=true "Downloading the files...")

And adds them to a database

![Alt text](/images/db1.png?raw=true "Downloading the files...")

Saving not just the title, but the number of pages, the search terms used, the number of times these terms were found, publication date (inferred from the title) and the document text as well. This way you can quickly find the most relevant documents.

![Alt text](/images/db2.png?raw=true "Downloading the files...")

The program extract the text surrounding the occurance of each search term (capitalizing the terms themselves for easier readability) allowing you to quickly find the relevant portions of each document or ascertain if the document is relevant to your studies. The full document text is avaible as well. 

![Alt text](/images/summary.png?raw=true "Downloading the files...")

# Will there be a GUI interface? 

Yes. I am working on a django based interface that should make searching through the results a breeze. It will present a table that ranks all the pages on the 'normalized number of mentions' variable (the number of keyword occurances divided by the number of pages) and the user will be able to click on any article to view the article information, the relevant portions, the entire document text and a link to the file itself. 

# Does it work? 

Yes. I have it running as we speak and have worked through thousands of documents already. 

# I want to use this program, but for different research, can I use this program? 

Yes. The downloading and fetching process is based on the website of the archive, so you should replace thhose parts with your own code. 
The analyzer and summarizer should work on any pdf that you throw at it. I have created a seperate script that contains just the analyzer.











