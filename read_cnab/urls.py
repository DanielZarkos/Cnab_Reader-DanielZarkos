from django.urls import path
from .views import upload_file

urlpatterns = [
    path("cnab/", upload_file, name='cnab')
]