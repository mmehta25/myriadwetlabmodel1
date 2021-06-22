from django.urls import path
from . import views

urlpatterns = [
	path('', views.index, name='index'),
	path('mylabs/', views.UserLabsListView.as_view(), name='my-created'),
	#User lab links
	path('analysis/<int:pk>', views.labanalysislabview, name="lab-analysis"),
	path('lab/<int:pk>', views.LabDetailView.as_view(), name='lab-detail'),
	path('process/<pk>', views.ProcessInstanceDetailView.as_view(), name='processinstance-detail'),
	##
	#Create a new lab
	path('createnew/', views.processinstrumentlist, name='create-new'),
	path('createnew/templates', views.templatelist, name='template-list'),
	#Update links
	path('analysis/<int:lab_id>/edit_instrument/<uuid:pk>', views.edit_instrument, name='edit-instrument'),
	#path('templateupdate/<int:pk>', views.templatedetail, name='template-update'),
	path('createnew/addinstrument', views.InstrumentCreate.as_view(), name='instrument-add'),
	path('createnew/addprocess', views.ProcessCreate.as_view(), name='process-add'),
	path('lab/create/', views.LabCreate.as_view(), name='lab-create'),
    path('lab/<int:pk>/update/', views.LabUpdate.as_view(), name='lab-update'),
    ##
	#Specific to the newly created lab (in form)
	path('assays/<int:pk>', views.AssayList.as_view(), name="lab-assay-list"),
	path('assays/add_assay/<int:pk>', views.AssayProcessInstanceCreate.as_view(), name="lab-assay-add"),
	path('assays/<int:pk_lab>/<int:pk_pi>', views.InstrumentInstanceAddView.as_view(), name="instrument-form"),
	##
]