from django.shortcuts import get_object_or_404, render
from .models import Lab, Assay, Process, ProcessInstance, Instrument, InstrumentInstance
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views import generic
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic import ListView, TemplateView
from django.urls import reverse_lazy
from django.urls import reverse
from django.forms.models import inlineformset_factory
from .forms import AssayFormSet
from django.shortcuts import redirect
# Create your views here.
def index(request):
    """View function for home page of site."""

    # Generate counts of some of the main objects
    num_labs = Lab.objects.all().count()
    num_instrument_types = Instrument.objects.all().count()

    # Available books (status = 'a')
    #num_instances_available = BookInstance.objects.filter(status__exact='a').count()

    # The 'all()' is implied by default.
    #num_authors = Author.objects.count()

    context = {
        'num_labs': num_labs,
        'num_instrument_types': num_instrument_types,
        # 'num_instances_available': num_instances_available,
        # 'num_authors': num_authors,
    }

    # Render the HTML template index.html with the data in the context variable
    return render(request, 'index.html', context=context)

def create_new(request):
    """View function for home page of site."""
    return render(request, 'create_new.html')

class UserLabsListView(LoginRequiredMixin,generic.ListView):
    """Generic class-based view listing labs created by current user."""
    model = Lab
    template_name ='labmodel/user_labs.html'

    def get_queryset(self):
        return Lab.objects.filter(creator=self.request.user)

class LabDetailView(generic.DetailView):
    model = Lab

class ProcessInstanceDetailView(generic.DetailView):
    model = ProcessInstance
# class LabListView(generic.ListView):
#     model = Lab
#     context_object_name = 'my_lab_list'   # your own name for the list as a template variable
#     #queryset = Book.objects.filter(title__icontains='war')[:5] # Get 5 books containing the title war
#     template_name = 'labs/lab_list.html'  # Specify your own template name/location

# Forms ##########################################################
class AssayAddView(TemplateView):
	template_name = "add_assay.html"
	# Define method to handle GET request
	def get(self, *args, **kwargs):
		# Create an instance of the formset
		formset = AssayFormSet(queryset=Assay.objects.none())
		return self.render_to_response({'assay_formset': formset})
	# Define method to handle POST request
	def post(self, *args, **kwargs):
		formset = AssayFormSet(data=self.request.POST)
		# Check if submitted forms are valid
		if formset.is_valid():
			formset.save()
			return redirect(reverse_lazy("my-created"))
		return self.render_to_response({'assay_formset': formset})

class LabCreate(CreateView):
	model = Lab
	fields = ['name', 'creator', 'days_per_month', 'integrated_hours', 'walkup_hours']
	#initial = {'date_of_death': '11/06/2020'}
	def get_success_url(self):
		return reverse("add_assay")

class LabUpdate(UpdateView):
    model = Lab
    fields = '__all__' # Not recommended (potential security issue if more fields added)