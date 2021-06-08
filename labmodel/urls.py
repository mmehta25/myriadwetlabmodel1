from django.urls import path
from . import views

urlpatterns = [
	path('', views.index, name='index'),
	path('mylabs/', views.UserLabsListView.as_view(), name='my-created'),
	path('createnew/', views.create_new, name='create-new'),
	path('lab/create/', views.LabCreate.as_view(), name='lab-create'),
    path('lab/<int:pk>/update/', views.LabUpdate.as_view(), name='lab-update'),
]