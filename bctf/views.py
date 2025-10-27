##

from django.shortcuts import render

def FrontPage (request):
    return render (request, "index.html", {})

def Scores (request):
    pass 
