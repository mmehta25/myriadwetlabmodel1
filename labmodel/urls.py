from django.urls import path

from . import views

urlpatterns = [
	#General urls not associated with a lab
	path('', views.index, name='index'),
	path('snow', views.failurerate_snowflake, name='snowflake'),
	path('snow2', views.offsetdata_snowflake2, name='snowflake2'),
	

	#User lab links
	path('mylabs/', views.UserLabsListView.as_view(), name='my-created'),
	path('analysis/<int:pk>', views.LabAnalysisLabView.as_view(), name="lab-analysis"),
	path('analysis/hours/<int:pk>', views.instrumentutilhours, name="inst-hours"),
	path('analysis/samples/<int:pk>', views.instrumentutilsamples, name="inst-samples"),
	path('analysis/schedule/<int:pk>', views.scheduleview, name="schedule"),
	path('lab/<int:pk>', views.LabDetailView.as_view(), name='lab-detail'),
	path('process/<pk>', views.ProcessInstanceDetailView.as_view(), name='processinstance-detail'),
	
	#Create a new lab
	path('createnew/', views.createnew, name='create-new'),
	path('createnew/templates', views.templatelist, name='template-list'),
	path('makeclone/<int:pk>', views.make_clone, name='make-clone'),

	#Update lab urls
	path('process/<p_id>/edit_instrument/<uuid:pk>', views.edit_instrument, name='edit-instrument'),
	path('analysis/<int:lab_id>/add_process/<int:assay_id>', views.add_process, name='add-process'),
	path('mylabs/<int:pk>/delete', views.LabDelete.as_view(), name='lab-delete'),
	path('createnew/addinstrument/<int:pk>', views.InstrumentAddView.as_view(), name='instrument-add'),
	path('createnew/addprocess/<int:pk>', views.ProcessCreate.as_view(), name='process-add'),
	path('lab/create/', views.LabCreate.as_view(), name='lab-create'),
    path('lab/<int:pk>/update/', views.LabUpdate.as_view(), name='lab-update'),

	#Specific to the newly created lab (in form)
	path('addclasses/<int:pk>', views.processinstrumentclassadd, name='class-add'),
	path('assays/<int:pk>', views.AssayList.as_view(), name="lab-assay-list"),
	path('assays/add_assay/<int:pk>', views.AssayProcessInstanceCreate.as_view(), name="lab-assay-add"),
	path('assays/<int:pk_lab>/instrument/<int:pk_inst>', views.InstrumentInstanceAddView.as_view(), name="instrument-form"),
	##
]