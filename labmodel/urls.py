from django.urls import path
from . import views

urlpatterns = [
	path('', views.index, name='index'),
	path('mylabs/', views.UserLabsListView.as_view(), name='my-created'),
	path('lab/<int:pk>', views.LabDetailView.as_view(), name='lab-detail'),
	path('process/<uuid:pk>', views.ProcessInstanceDetailView.as_view(), name='processinstance-detail'),
	path('createnew/', views.create_new, name='create-new'),
	path('add_assay', views.AssayAddView.as_view(), name="add_assay"),
	path('lab/create/', views.LabCreate.as_view(), name='lab-create'),
    path('lab/<int:pk>/update/', views.LabUpdate.as_view(), name='lab-update'),
]