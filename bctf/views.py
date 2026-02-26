##

from django.shortcuts import render

def FrontPage (request):
    return render (request, "index.html", {'the': 'Hewwo'})

def Scores (request):
    pass 
