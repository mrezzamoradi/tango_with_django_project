from django.shortcuts import render
from rango.models import Category, Page

# Create your views here.


def index(request):
    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]
    context_dic = {'categories': category_list, 'pages': page_list}
    return render(request, 'rango/index.html', context=context_dic)


def about(request):
    context_dic = {'name': 'Reza Moradi'}
    return render(request, 'rango/about.html', context=context_dic)


def show_category(request, category_name_slug):

    context_dic = {}
    try:
        category = Category.objects.get(slug=category_name_slug)
        pages = Page.objects.filter(category=category)
        context_dic['pages'] = pages
        context_dic['category'] = category

    except Category.DoesNotExist:
        context_dic['pages'] = None
        context_dic['category'] = None

    return render(request, 'rango/category.html', context=context_dic)

