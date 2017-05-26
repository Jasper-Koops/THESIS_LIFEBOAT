# THESIS_LIFEBOAT

# Before we get started

This program is still very much a work in progress, that is being used and developed simultaneously.
As such, the code is still of a rather poor quality with a lot of 'hackey' solutions to the problems that have emerged. 
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


