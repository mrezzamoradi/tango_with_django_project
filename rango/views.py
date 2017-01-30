from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.


def index(request):
    context_dic = {'boldmessage': "Crunchy, creamy, cookie, candy, cupcake!"}
    return render(request, 'rango/index.html', context=context_dic)


def about(request):
    context_dic = {'name': 'Reza Moradi'}
    return render(request, 'rango/about.html', context=context_dic)