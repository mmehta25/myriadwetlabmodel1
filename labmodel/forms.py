from django.forms import ModelForm, inlineformset_factory, modelformset_factory
from .models import Assay, ProcessInstance, Instrument, InstrumentInstance, Lab
from django import forms
from .widgets import RangeInput

class AssayForm(ModelForm):
    class Meta:
        model = Assay
        exclude = ()

class ProcessInstanceForm(ModelForm):
    class Meta:
        model = ProcessInstance
        exclude = ()

ProcessInstanceFormSet = inlineformset_factory(Assay, ProcessInstance,
                                            form=ProcessInstanceForm, extra=1)
class InstrumentForm(ModelForm):
    class Meta:
      model = Instrument
      fields = ['name',]

InstrumentFormSet = modelformset_factory(
    Instrument, fields=("name",), extra=1
)

class InstrumentInstanceForm(ModelForm):
    class Meta:
      model = InstrumentInstance
      fields = ['instrument', 'samples_per_day', 'integrated_or_walkup']

InstrumentInstanceFormSet = modelformset_factory(
    InstrumentInstance, fields=("instrument", 'samples_per_day', 'identical_copies', 'integrated_or_walkup'), extra=1
)
#Edit on new page forms
class EditInstrumentForm(ModelForm):
    class Meta:
        model = InstrumentInstance
        fields = ('identical_copies', 'samples_per_day')
        widgets = {"identical_copies": RangeInput(attrs={"min": 1, "max": 10, "step": 1, "id": "myInstrumentSlider"})}
        help_texts = {'identical_copies': None,}

class AddProcessForm(ModelForm):
    class Meta:
        model = ProcessInstance
        fields = ('subname', 'assay', 'instrument', 'process', 'duration', 'sample_count', )
        widgets = {"sample_count": RangeInput(attrs={"min": 1, "max": 100, "step": 1, "id": "mySampleCountSlider"}) }
        help_texts = {'sample_count': None,}
#Dropdown Forms
class OffsetSliderForm(ModelForm):
    class Meta:
        model = Lab
        fields = ('offset', )
        widgets = {"offset": RangeInput(attrs={"min": 1, "max": 5, "id": "mySlider"}) }
        help_texts = {
            'offset': None,
        }
class ProcessDropdownForm(ModelForm):
    class Meta:
        model = ProcessInstance
        fields = ('duration', 'sample_count' )

class Labname_form(ModelForm):
    class Meta:
        model = Lab
        fields = ('name', )
        help_texts = {
            'name': "Rename Lab Here",
        }
class LabAssumptionsDropdownForm(ModelForm):
    class Meta:
        model = Lab
        fields = ('offset', 'current_year', 'max_utilization', 'integrated_hours', 'walkup_hours', 'days_per_month' )
        widgets = {"offset": RangeInput(attrs={"min": 1, "max": 5, "id": "mySlider"}) }
        help_texts = {
            'offset': None,
        }

