from django.urls import path
from .views import CallbackView, CancelView

app_name = 'kentapay'

urlpatterns = [
    path('callback/', CallbackView.as_view(), name='callback'),
    path('cancel/', CancelView.as_view(), name='cancel'),
]
