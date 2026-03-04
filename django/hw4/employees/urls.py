from django.urls import path

from . import views

app_name = "employees"

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("employees/", views.EmployeeListView.as_view(), name="list"),
    path("employees/<int:pk>/", views.EmployeeDetailView.as_view(), name="detail"),
]
