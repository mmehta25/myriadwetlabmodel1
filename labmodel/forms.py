from django.forms import modelformset_factory
from .models import Assay

AssayFormSet = modelformset_factory(
    Assay, fields=('name', 'lab'), extra=1
)