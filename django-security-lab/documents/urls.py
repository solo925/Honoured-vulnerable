"""documents/urls.py"""
from django.urls import path
from . import views

urlpatterns = [
    path("upload/",             views.upload_document,  name="doc_upload"),
    path("list/",               views.list_documents,   name="doc_list"),
    path("download/<int:doc_id>/", views.download_document, name="doc_download"),
    path("delete/<int:doc_id>/",   views.delete_document,   name="doc_delete"),
]
