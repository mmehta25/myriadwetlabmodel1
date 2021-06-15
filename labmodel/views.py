from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect
from .models import Lab, Assay, Process, ProcessInstance, Instrument, InstrumentInstance
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic import ListView, TemplateView
from django.urls import reverse_lazy
from django.urls import reverse
from django.forms.models import inlineformset_factory
from .forms import ProcessInstanceFormSet, InstrumentInstanceFormSet
from django.shortcuts import redirect
from django.db import transaction
from django.contrib.auth.models import User
from django import forms

# Create your views here.
def index(request):
    """View function for home page of site."""

    # Generate counts of some of the main objects
    num_labs = Lab.objects.all().count()
    num_instrument_types = Instrument.objects.all().count()

    context = {
        'num_labs': num_labs,
        'num_instrument_types': num_instrument_types,
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)

class UserLabsListView(LoginRequiredMixin,generic.ListView):
    """Generic class-based view listing labs created by current user."""
    model = Lab
    template_name ='labmodel/user_labs.html'

    def get_queryset(self):
        return Lab.objects.filter(creator=self.request.user)

def processinstrumentlist(request):
    """Generic class-based view listing all Processes and Instruments"""
    context = {
    'process_list': Process.objects.all(),
    'instrument_list': Instrument.objects.all()
    }
    return render(request, 'create_new.html', context=context)

class LabDetailView(generic.DetailView):
    model = Lab

class ProcessInstanceDetailView(generic.DetailView):
    model = ProcessInstance

# Forms ##########################################################
class AssayList(LoginRequiredMixin, ListView):
    model = Assay
    template_name ='labmodel/assay_list.html'
    def get_context_data(self, **kwargs):
        data = super(AssayList, self).get_context_data(**kwargs)
        data['lab_id'] = self.kwargs['pk']
        lab = get_object_or_404(Lab, pk=self.kwargs['pk'])
        data['lab_name'] = lab.name
        return data

    def get_queryset(self):
        return Assay.objects.filter(lab_id=self.kwargs['pk'])

class AssayCreate(CreateView):
    model = Assay
    fields = ['name', 'lab']

# class ProcessCreate(CreateView):
#     model = Process
#     fields = ['name', ]
# class InstrumentCreate(CreateView):
#     model = Instrument
#     fields = ['name', ]

class AssayProcessInstanceCreate(CreateView):
    model = Assay
    fields = ['name', 'lab']

    def get_initial(self):
        lab = get_object_or_404(Lab, pk=self.kwargs['pk'])
        return {
            'lab': lab
        }

    def get_success_url(self):
        return reverse("lab-assay-list", args=(self.kwargs['pk'],))

    def get_context_data(self, **kwargs):
        data = super(AssayProcessInstanceCreate, self).get_context_data(**kwargs)
        if self.request.POST:
            data['processinstances'] = ProcessInstanceFormSet(self.request.POST)
        else:
            data['processinstances'] = ProcessInstanceFormSet()
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        processinstances = context['processinstances']
        with transaction.atomic():
            self.object = form.save()
            if processinstances.is_valid():
                processinstances.instance = self.object
                processinstances.save()
        return super(AssayProcessInstanceCreate, self).form_valid(form)

class LabCreate(CreateView):
    model = Lab
    fields = ['name', 'creator', 'days_per_month', 'offset', 'integrated_hours', 'walkup_hours', 'max_utilization', 
    'projection_for_2021', 'projection_for_2022', 'projection_for_2023', 'projection_for_2024', 
    'projection_for_2025', 'projection_for_2026']

    def get_initial(self):
        user = get_object_or_404(User, username=self.request.user.username)
        return {
            'creator': user
        }
    def form_valid(self, form):
        if form.is_valid():
            self.object = form.save()
            return HttpResponseRedirect(self.get_success_url(self.object.pk))

    def get_success_url(self, lab_id):
        return reverse("lab-assay-add", args=(lab_id,))

class InstrumentInstanceAddView(TemplateView):
    template_name = "labmodel/instrumentinstance_form.html"

    # Define method to handle GET request
    def get(self, *args, **kwargs):
        # Create an instance of the formset
        processinstance = get_object_or_404(ProcessInstance, pk=self.kwargs['pk_pi'])
        formset = InstrumentInstanceFormSet(queryset=InstrumentInstance.objects.none(), initial = [{'processinstance': processinstance}])
        return self.render_to_response({'instrumentinstance_formset': formset})

    def post(self, *args, **kwargs):
        formset = InstrumentInstanceFormSet(data=self.request.POST)
        # Check if submitted forms are valid
        if formset.is_valid():
            formset.save()
            return redirect(reverse("lab-assay-list", args=(self.kwargs['pk_lab'], )))

        return self.render_to_response({'instrumentinstance_formset': formset})

class LabUpdate(UpdateView):
    model = Lab
    fields = '__all__' # Not recommended (potential security issue if more fields added)