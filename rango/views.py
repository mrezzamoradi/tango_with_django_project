from django.shortcuts import render, get_object_or_404, redirect
from rango.models import Category, Page
from rango.forms import CategoryForm, PageForm, UserForm, UserProfileForm
# from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.core.urlresolvers import reverse
from datetime import datetime
from registration.backends.simple.views import RegistrationView
from django.core import serializers


# Create your views here.


def index(request):
    category_list = Category.objects.order_by('-likes')[:5]
    page_list = Page.objects.order_by('-views')[:5]
    context_dic = {'categories': category_list, 'pages': page_list}

    visitor_cookie_handler(request)
    context_dic['visits'] = request.session['visits']

    if (request.method == 'GET') and ('cat_search' in request.GET):
        query = request.GET['cat_search']
        matched = Category.objects.filter(name__contains=query)
        return HttpResponse(serializers.serialize('json', matched))

    return render(request, 'rango/index.html', context=context_dic)


def about(request):
    context_dic = {'name': 'Reza Moradi'}

    visitor_cookie_handler(request)
    context_dic['visits'] = request.session['visits']

    return render(request, 'rango/about.html', context=context_dic)


def show_category(request, category_name_slug):
    context_dic = {}
    try:
        category = Category.objects.get(slug=category_name_slug)
        pages = Page.objects.filter(category=category)
        context_dic['pages'] = pages
        context_dic['category'] = category
        category.views += 1
        category.save()

        if (request.method == 'GET') and ('like' in request.GET):
            category.likes += 1
            category.save()
            return HttpResponse(category.likes)

    except Category.DoesNotExist:
        context_dic['pages'] = None
        context_dic['category'] = None

    return render(request, 'rango/category.html', context=context_dic)


@login_required
def add_category(request):
    form = CategoryForm()

    if request.method == 'POST':
        form = CategoryForm(request.POST)

        if form.is_valid():
            form.save(commit=True)
            return index(request)
        else:
            print(form.errors)

    return render(request, 'rango/add_category.html', {'form': form})


@login_required
def add_page(request, category_name_slug):
    form = PageForm()
    category = get_object_or_404(Category, slug=category_name_slug)

    if request.method == 'POST':
        form = PageForm(request.POST)

        if form.is_valid():
            page = form.save(commit=False)
            page.category = category
            page.views = 0
            page.save()
            return show_category(request, category_name_slug)
        else:
            print(form.errors)

    return render(request, 'rango/add_page.html', {'form': form, 'category': category})


def register_profile(request):
    # registered = False

    if request.method == 'POST':
        # user_form = UserForm(request.POST)
        profile_form = UserProfileForm(request.POST)

        if profile_form.is_valid():
            # user = user_form.save()
            # user.set_password(user.password)
            # user.save()

            user = request.user
            profile = profile_form.save(commit=False)
            profile.user = user

            if 'picture' in request.FILES:
                profile.picture = request.FILES['picture']

            profile.save()
            # registered = True
        else:
            print(profile_form.errors)

    else:
        profile_form = UserProfileForm()

    return render(request, 'rango/register.html', {
        # 'user_form': user_form,
        'profile_form': profile_form,
        # 'registered': registered
    })


# def user_login(request):
#     if request.method == 'POST':
#         username = request.POST.get('username')
#         password = request.POST.get('password')
#
#         user = authenticate(username=username, password=password)
#
#         if user:
#             if user.is_active:
#                 login(request, user)
#                 return HttpResponseRedirect(reverse('rango:index'))
#             else:
#                 return HttpResponse('Your Rango account is disabled.')
#         else:
#             print('Invalid login details: {0}, {1}'.format(username, password))
#             return HttpResponse('Invalid login details supplied')
#     else:
#         return render(request, 'rango/login.html', {})


# @login_required
# def user_logout(request):
#     logout(request)
#     return HttpResponseRedirect(reverse('rango:index'))


def get_server_side_cookie(request, cookie, default_val=None):
    val = request.session.get(cookie)
    if not val:
        val = default_val
    return val


def visitor_cookie_handler(request):
    visits = int(get_server_side_cookie(request, 'visits', '1'))
    last_visit_cookie = get_server_side_cookie(request, 'last_visit', str(datetime.now()))
    last_visit_time = datetime.strptime(last_visit_cookie[:-7], '%Y-%m-%d %H:%M:%S')

    if (datetime.now() - last_visit_time).seconds > 0:
        visits += 1
        request.session['last_visit'] = str(datetime.now())
    else:
        visits = 1
        request.session['last_visit'] = last_visit_cookie

    request.session['visits'] = visits


class MyRegistrationView(RegistrationView):
    def get_success_url(self, user=None):
        self.success_url = 'http://www.google.com'
        return 'http://www.google.com'


def track_url(request):
    page_id = None

    if (request.method == 'GET') and ('page_id' in request.GET):
        page_id = request.GET['page_id']

    try:
        page = Page.objects.get(id=page_id)
        page.views += 1
        page.save()
        return redirect(page.url)
    except Page.DoesNotExist:
        print('Page with ID: {0} not found.'.format(page_id))
        return HttpResponseRedirect(reverse('rango:index'))
