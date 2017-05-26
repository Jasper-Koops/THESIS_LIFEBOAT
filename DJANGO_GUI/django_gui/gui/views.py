from django.shortcuts import render
from .models import SavedData

# Create your views here.



def database(request):
    """displays the database list"""

    #entries = Entry.objects.all().order_by('-rating')  #Hier dus normalized?
    documents = SavedData.objects.all().order_by('-normalized_number_of_mentions')

    return render(request, 'gui/database.html', {'database': documents})
    # return render(request, 'interface/database.html')


def document_detail(request, id):
    """Displays the document overview"""

    document = SavedData.objects.get(row_id=id)
    abstract_list = []
    for paragraph in document.abstracts.split('\n'):
        abstract_list.append(paragraph)

    return render(request, 'gui/document_detail.html', {
    'document': document, 'abstracts': abstract_list})


def saved_docs(request):
    documents = SavedData.objects.filter(read_status = 1)
    return render(request, 'gui/saved_docs.html', {'database': documents})
