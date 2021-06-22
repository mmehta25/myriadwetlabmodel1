from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse, HttpResponseRedirect
from .models import Lab, Assay, Process, ProcessInstance, Instrument, InstrumentInstance, LabAnalysis
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
import pandas as pd
import plotly.express as px
from plotly.offline import plot
from labmodel.forms import EditInstrumentForm, OffsetSliderForm

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
def templatelist(request):
    context = {

    }
    return render(request, 'template_list.html', context=context)

class LabDetailView(generic.DetailView):
    model = Lab

class ProcessInstanceDetailView(generic.DetailView):
    model = ProcessInstance

def labanalysislabview(request, pk):
    obj = LabAnalysis(lab=get_object_or_404(Lab, pk=pk))
    obj.save()

    util_dict_samples = {}
    util_dict_hours = {}
    years = [2021, 2022, 2023, 2024, 2025, 2026]
    instrument_set = set()
    for assay in obj.lab.assay_set.all():
        for processinstance in assay.processinstance_set.all():
            for instrumentinstance in processinstance.instrumentinstance_set.all():
                instrument_set.add(instrumentinstance.instrument)

    for yr in years:
        for instrument in instrument_set:
            bysamples = obj.instrument_utilization_samples(instrument, yr)
            byhours = obj.instrument_utilization_hours(instrument, yr)

            if bysamples > 1:
                bysamples = 1

            if byhours > 1:
                byhours = 1

            if instrument in util_dict_samples:
                util_dict_samples[instrument].append(bysamples)
            else:
                util_dict_samples[instrument] = [bysamples]

            if instrument in util_dict_hours:
                util_dict_hours[instrument].append(byhours)
            else:
                util_dict_hours[instrument] = [byhours]
    names = []
    for instrument in instrument_set:
        names.append(instrument.name)

    max_util = obj.lab.max_utilization / 100

    df_samples = pd.DataFrame.from_dict(util_dict_samples, orient='index', columns=years)
    df_hours = pd.DataFrame.from_dict(util_dict_hours, orient='index', columns=years)
    
    data_samples = df_samples.values
    data_hours = df_hours.values

    fig_samples = px.imshow(data_samples,
        labels=dict(x="Year", y="Instrument", color="Utilization"),
                x=years,
                y=names, 
                range_color=[0,1],
                color_continuous_scale=[(0.00, "rgb(51, 51, 204)"),   (0.10, "rgb(51, 51, 204)"),
                                        (0.10, "rgb(102, 0, 255)"),   (0.20, "rgb(102, 0, 255)"),
                                        (0.20, "rgb(153, 51, 255)"),   (0.30, "rgb(153, 51, 255)"),
                                        (0.30, "rgb(204, 0, 255)"),   (0.40, "rgb(204, 0, 255)"),
                                        (0.40, "rgb(204, 0, 204)"),   (0.50, "rgb(204, 0, 204)"),
                                        (0.50, "rgb(204, 0, 102)"),   (0.60, "rgb(204, 0, 102)"),
                                        (0.60, "rgb(255, 80, 80)"), (max_util, "rgb(255, 80, 80)"),
                                        (max_util, "rgb(204, 0, 0)"),  (1.00, "rgb(204, 0, 0)")]
               )
    fig_samples.update_xaxes(side="top")
    plot_div_samples = plot(fig_samples, output_type='div')
    for y in years:
        df_samples[y] = pd.Series(["{0:.2f}%".format(val * 100) for val in df_samples[y]], index = df_samples.index)
    df_htmldiv_samples = df_samples.to_html(classes=["table", "table-hover"])

    fig_hours = px.imshow(data_hours,
        labels=dict(x="Year", y="Instrument", color="Utilization"),
                x=years,
                y=names, 
                range_color=[0,1],
                color_continuous_scale=[(0.00, "rgb(51, 51, 204)"),   (0.10, "rgb(51, 51, 204)"),
                                        (0.10, "rgb(102, 0, 255)"),   (0.20, "rgb(102, 0, 255)"),
                                        (0.20, "rgb(153, 51, 255)"),   (0.30, "rgb(153, 51, 255)"),
                                        (0.30, "rgb(204, 0, 255)"),   (0.40, "rgb(204, 0, 255)"),
                                        (0.40, "rgb(204, 0, 204)"),   (0.50, "rgb(204, 0, 204)"),
                                        (0.50, "rgb(204, 0, 102)"),   (0.60, "rgb(204, 0, 102)"),
                                        (0.60, "rgb(255, 80, 80)"), (max_util, "rgb(255, 80, 80)"),
                                        (max_util, "rgb(204, 0, 0)"),  (1.00, "rgb(204, 0, 0)")]
               )
    fig_hours.update_xaxes(side="top")
    plot_div_hours = plot(fig_hours, output_type='div')
    for y in years:
        df_hours[y] = pd.Series(["{0:.2f}%".format(val * 100) for val in df_hours[y]], index = df_hours.index)
    df_htmldiv_hours = df_hours.to_html(classes=["table", "table-hover"])

    lab = get_object_or_404(Lab, pk=pk)
    if request.method == 'POST':
        form = OffsetSliderForm(request.POST)
        if form.is_valid():
            lab.offset = form.cleaned_data['offset']
            lab.save()
            return HttpResponseRedirect(reverse('lab-analysis', args=(pk, )) )
    else:
        form = OffsetSliderForm()

    context = {
    'lab_analysis': obj,
    'offsetslider_form': form,
    'lab': obj.lab,
    'lab_id': obj.lab.pk,
    'plot_div_samples': plot_div_samples,
    'df_samples': df_htmldiv_samples,
    'plot_div_hours': plot_div_hours,
    'df_hours': df_htmldiv_hours
    }
    return render(request, 'labmodel/lab_analysis.html', context=context)


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
    fields = ['name', 'lab', 'projection_for_2021', 'projection_for_2022', 'projection_for_2023', 'projection_for_2024', 
    'projection_for_2025', 'projection_for_2026']

class AssayProcessInstanceCreate(CreateView):
    model = Assay
    fields = ['name', 'lab', 'projection_for_2021', 'projection_for_2022', 'projection_for_2023', 'projection_for_2024', 
    'projection_for_2025', 'projection_for_2026']

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
    fields = ['name', 'creator', 'days_per_month', 'offset', 'integrated_hours', 'walkup_hours', 'max_utilization']

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

class InstrumentCreate(CreateView):
    model = Instrument
    fields = ['name', ]

    def get_success_url(self):
        return reverse("create-new")
class ProcessCreate(CreateView):
    model = Process
    fields = ['name', ]

    def get_success_url(self):
        return reverse("create-new")

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

def edit_instrument(request, lab_id, pk):
    instrument_instance = get_object_or_404(InstrumentInstance, pk=pk)

    # If this is a POST request then process the Form data
    if request.method == 'POST':

        # Create a form instance and populate it with data from the request (binding):
        form = EditInstrumentForm(request.POST)

        # Check if the form is valid:
        if form.is_valid():
            # process the data in form.cleaned_data as required (here we just write it to the model due_back field)
            instrument_instance.identical_copies= form.cleaned_data['identical_copies']
            instrument_instance.save()

            # redirect to a new URL:
            return HttpResponseRedirect(reverse('lab-analysis', args=(lab_id, )) )

    # If this is a GET (or any other method) create the default form.
    else:
        form = EditInstrumentForm()

    context = {
        'form': form,
        'instrument_instance': instrument_instance,
    }

    return render(request, 'labmodel/edit_instrument.html', context)
