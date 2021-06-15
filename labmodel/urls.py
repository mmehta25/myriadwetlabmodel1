from django.urls import path
from . import views

urlpatterns = [
	path('', views.index, name='index'),
	path('mylabs/', views.UserLabsListView.as_view(), name='my-created'),
	path('lab/<int:pk>', views.LabDetailView.as_view(), name='lab-detail'),
	path('process/<pk>', views.ProcessInstanceDetailView.as_view(), name='processinstance-detail'),
	path('createnew/', views.processinstrumentlist, name='create-new'),
	#specific to the newly created lab
	path('assays/<int:pk>', views.AssayList.as_view(), name="lab-assay-list"),
	path('assays/add_assay/<int:pk>', views.AssayProcessInstanceCreate.as_view(), name="lab-assay-add"),
	##
	path('assays/<int:pk_lab>/<int:pk_pi>', views.InstrumentInstanceAddView.as_view(), name="instrument-form"),
	
	path('lab/create/', views.LabCreate.as_view(), name='lab-create'),
    path('lab/<int:pk>/update/', views.LabUpdate.as_view(), name='lab-update'),
]