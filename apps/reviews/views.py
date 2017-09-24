# TODO: prettify, move all model logic to models.py, and deploy
from django.shortcuts import render, HttpResponse, redirect
from django.contrib import messages
import bcrypt
from .models import *

def home(request):
    init_session(request)
    if request.session['user_id'] != "":
        return redirect("/books")
    context = {
        'name': request.session['name'],
        'alias': request.session['alias'],
        'email': request.session['email']
    }
    return render(request, "home.html", context)

def register(request):
    init_session(request)
    if request.session['user_id'] != "":
        return redirect("/books")
    if request.method == "POST":
        request.session['alias'] = request.POST['alias']
        register_result = User.objects.register(request.POST)
        errors = register_result['errors']
        if len(errors):
            for tag, error in errors.iteritems():
                messages.error(request, error)
            request.session['name'] = request.POST['name']
            request.session['email'] = request.POST['email']
        else:
            request.session['user_id'] = register_result['user'].id
            return redirect("/books")
    return redirect("/")

def login(request):
    init_session(request)
    if request.session['user_id'] != "":
        return redirect("/books")
    if request.method == "POST":
        login_result = User.objects.login(request.POST)
        errors = login_result['errors']
        if len(errors):
            for tag, error in errors.iteritems():
                messages.error(request, error)
            request.session['email'] = request.POST['email']
        else:
            request.session['user_id'] = login_result['user'].id
            request.session['alias'] = login_result['user'].alias
            return redirect("/books")
    return redirect("/")  

def books(request):
    init_session(request)
    if request.session['user_id'] == "":
        return redirect("/")
    reviews = Review.objects.order_by("-created_at")[:3] # does this order need to be reversed???
    books = Book.objects.filter()
    context = {
        'alias': request.session['alias'],
        'books': books,
        'reviews': reviews
    }
    return render(request, "books.html", context)

def book_form(request):
    init_session(request)
    if request.session['user_id'] == "":
        return redirect("/")
    authors = Author.objects.all()
    context = {
        'title': request.session['title'],
        'new_author': request.session['new_author'],
        'stars': request.session['stars'],
        'review': request.session['review'],
        'user_id': request.session['user_id'],
        'authors': authors
    }
    return render(request, "new.html", context)

def new_book(request):
    init_session(request)
    if request.session['user_id'] == "":
        return redirect("/")  
    if request.method == "POST":  
        book = None
        add_book_result = Book.objects.add_book(request.POST)
        errors = add_book_result['errors']
        if len(errors):
            for tag, error in errors.iteritems():
                messages.error(request, error, extra_tags=tag)
                return redirect("/books/add")       
            request.session['title'] = request.POST['title']
            request.session['review'] = request.POST['review']
            request.session['stars'] = request.POST['stars']
        else:
            request.session['title'] = ""
            request.session['review'] = ""
            request.session['stars'] = "5"
            return redirect("/books/" + str(add_book_result['book'].id))
    return redirect('/books/add')

def book(request, id):
    init_session(request)
    if request.session['user_id'] == "":
        return redirect("/")  
    book = Book.objects.get(id=id)
    reviews = book.reviews.all()
    print reviews
    context = {
        'book': book,
        'user_id': request.session['user_id'],
        'reviews': reviews
    }
    return render(request, "book.html", context)

def user(request, id):
    init_session(request)
    if request.session['user_id'] == "":
        return redirect("/")  
    user = User.objects.get(id=id)
    reviews = user.reviews.all()
    context = {
        'user': user,
        'reviews': reviews,
        'count': len(reviews)
    }
    return render(request, "user.html", context)

def delete(request, book_id, id):
    init_session(request)
    if request.session['user_id'] == "":
        return redirect("/")      
    review = Review.objects.get(id=id)
    if request.session['user_id'] != review.reviewer.id:
        return redirect("/")
    else:
        Review.objects.get(id=id).delete()
        if Book.objects.get(id=book_id).reviews.count() == 0:
            Book.objects.get(id=book_id).delete()
            return redirect("/books")
        return redirect("/books/" + book_id)

def new_review(request, id):
    init_session(request)
    if request.session['user_id'] == "":
        return redirect("/")   
    errors = Review.objects.add_review(request.POST)
    if len(errors): # if posting the new review went awry
        for tag, error in errors.iteritems():
            messages.error(request, error, extra_tags=tag)
        request.session['review'] = request.POST['review']
        request.session['stars'] = request.POST['stars']
    return redirect("/books/" + id)

def logout(request):
    reset_session(request)
    return redirect("/")

def init_session(request): 
    if not 'initialized' in request.session:
        request.session['initialized'] = True
        reset_session(request)

def reset_session(request):
     request.session['user_id'] = ""
     request.session['name'] = ""
     request.session['alias'] = ""
     request.session['email'] = ""
     request.session['review'] = ""
     request.session['title'] = ""
     request.session['new_author'] = ""
     request.session['stars'] = "3"
