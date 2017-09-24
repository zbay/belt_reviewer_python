from __future__ import unicode_literals
from django.db import models
import re
import bcrypt
import datetime

class UserManager(models.Manager):
    def register(self, postData):
        errors = {}
        emailRegex=re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$')
        alphaRegex = re.compile(r'^[a-zA-Z]+[ ]*[a-zA-Z]*$')
        dateRegex = re.compile(r'^([0][1-9]|1[0-2])\/([0-2][0-9]|3[0-1])\/\d{4}$') # too lazy to account for the differing days in months, allows 31 days for all months
        if (len(postData['name']) < 2) or (len(postData['name']) > 255):
            errors['name'] = "Names must be between 2 and 255 characters in length!"
        if (len(postData['alias']) < 2) or (len(postData['alias']) > 255):
            errors['alias'] = "An alias must be between 2 and 255 characters in length!"
        if not alphaRegex.match(postData['name']) or not alphaRegex.match(postData['alias']):
            errors['name'] = "Your name and alias can only contain alphabetical characters and spaces!"
        if not emailRegex.match(postData['email']):
            errors['email'] = "Your email is in an invalid format!"
        if (len(postData['email']) > 255):
            errors['email_length'] = "Your email address is too long!"
        if postData['password'] != postData['confirm_password']:
            errors['password_match'] = "Your passwords do not match!"
        if len(postData['password']) < 8:
            errors['password'] = "Your password must be at least 8 characters in length!"
        user = User.objects.filter(email=postData['email'])
        if len(user) > 0:
            errors['redundant'] = 'This email has already been taken! Please use a different address!'
        user = None
        if len(errors) == 0:
            hash1 = bcrypt.hashpw(postData['password'].encode(), bcrypt.gensalt())
            user = User.objects.create(name=postData['name'], alias=postData['alias'], email=postData['email'], password=hash1)
        return {'errors': errors, 'user': user}
    def login(self, postData):
        errors = {}
        user = User.objects.filter(email=postData['email'])
        if len(user) == 0:
            errors['missing'] = 'This email does not exist in the system! Maybe you need to sign up.'  
        else:
            if not bcrypt.checkpw(postData['password'].encode(), user[0].password.encode()): 
                errors['password'] = 'Your password is incorrect!'
        user = None
        if len(errors) == 0:
            user = User.objects.get(email=postData['email'])
        return {'errors': errors, 'user': user}
class User(models.Model):
    name = models.CharField(max_length=255)
    alias = models.CharField(max_length=255)
    email = models.CharField(max_length=255, unique=True)
    password = models.TextField()
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)
    objects = UserManager()

class AuthorManager(models.Manager):
    def validate_and_create(self, postData):
        errors = {}
        if (len(postData['new_author']) < 2) and (len(postData['existing_author']) < 2):
            errors['name'] = "Names must be at least 2 characters in length!"
        use_new = len(postData['new_author']) > 2 # defaults to using a newly inputted name, not a selected one
        name = postData['existing_author']
        if use_new:
            name = postData['new_author']
        author = Author.objects.filter(name=name)
        if len(author) == 0:
            author = Author.objects.create(name=name)
        else:
            author = Author.objects.get(name=name)
        return {'errors': errors, 'author': author}
class Author(models.Model):
    name = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)
    objects = AuthorManager()

class BookManager(models.Manager):
    def validator(self, postData):
        errors = {}
        if len(postData['title']) < 2:
            errors['title'] = "Titles must be at least 2 characters in length!"
        return errors
    def add_book(self, postData):
        errors = {}
        book = None
        addAuthor = False
        # 1. validate author, adding to database if not yet in there
        authorData = AuthorManager().validate_and_create(postData)
        authorErrors = authorData['errors']
        author = authorData['author']
        for key, error in authorErrors.items():
            errors[key] = error
        # 2. validate book
        bookErrors = self.validator(postData)
        for key, error in bookErrors.items():
            errors[key] = error
        # 3. validate review. 
        reviewErrors = ReviewManager().validator(postData)
        for key, error in reviewErrors.items():
            errors[key] = error
        if len(errors) == 0:
            # 4. Add author if necessary 5. Add book 
            book = Book.objects.create(title=postData['title'], author=author)
            # 6. Add review.
            reviewer = User.objects.get(id=postData['user_id'])
            Review.objects.create(text=postData['review'], stars=int(postData['stars']), book=book, reviewer=reviewer)
        return {'errors': errors, 'book': book}
class Book(models.Model):
    title = models.CharField(max_length=255)
    author = models.ForeignKey(Author, related_name="books")
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)
    objects = BookManager()

class ReviewManager(models.Manager):
    def validator(self, postData):
        errors = {}
        if len(postData['review']) < 2:
            errors['review'] = "Reviews must be at least 2 characters in length!"
        if int(postData['stars']) > 5 or int(postData['stars'] < 0):
            errors['stars'] = "Stars must be between 0 and 5!"
        return errors
    def add_review(self, postData):
        errors = self.validator(postData)
        if len(errors) == 0:
            user = User.objects.get(id=postData['user_id'])
            book = Book.objects.get(id=postData['book_id'])
            Review.objects.create(text=postData['review'], stars=int(postData['stars']), reviewer=user, book=book)
        return errors
class Review(models.Model):
    text = models.CharField(max_length=255)
    stars = models.IntegerField()
    book = models.ForeignKey(Book, related_name="reviews")
    reviewer = models.ForeignKey(User, related_name="reviews")
    created_at = models.DateTimeField(auto_now_add = True)
    updated_at = models.DateTimeField(auto_now = True)
    objects = ReviewManager()
