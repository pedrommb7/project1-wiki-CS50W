from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("wiki/<str:title>", views.entry, name="entry"),
    path("newPage", views.newPage, name="newPage"),
    path("wiki/", views.randomEntry, name="randomEntry"),
    path("wiki/<str:title>/edit", views.editEntry, name="editEntry"),
    path("wiki/<str:title>/submit", views.submitEditEntry, name="submitEditEntry"),
    path("search", views.search, name="search")
]
