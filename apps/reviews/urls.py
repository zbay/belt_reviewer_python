from django.conf.urls import url
from . import views
urlpatterns = [
  url(r'^$', views.home),
  url(r'^register$', views.register), #post
  url(r'^login$', views.login), #post
  url(r'^logout$', views.logout),
  url(r'^books$', views.books),
  url(r'^books/add$', views.book_form),
  url(r'^new_book$', views.new_book), #post
  url(r'^books/(?P<id>\d+)$', views.book),
  url(r'^users/(?P<id>\d+)$', views.user),
  url(r'^books/(?P<book_id>\d+)/delete/(?P<id>\d+)', views.delete),
  url(r'^books/(?P<id>\d+)/new_review$', views.new_review), #post
]