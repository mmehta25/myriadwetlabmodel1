from django.forms import ModelForm, inlineformset_factory, modelformset_factory
from .models import Assay, ProcessInstance, InstrumentInstance, Lab
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

class InstrumentInstanceForm(ModelForm):
    class Meta:
      model = InstrumentInstance
      fields = ['instrument', 'processinstance', 'samples_per_day', 'integrated_or_walkup']

InstrumentInstanceFormSet = modelformset_factory(
    InstrumentInstance, fields=("instrument", "processinstance",'samples_per_day', 'identical_copies', 'integrated_or_walkup'), extra=1
)

class EditInstrumentForm(ModelForm):
    class Meta:
        model = InstrumentInstance
        fields = ('identical_copies', )
        widgets = {"identical_copies": RangeInput(attrs={"min": 1, "max": 10, "step": 1, "id": "myInstrumentSlider"}) }
        help_texts = {'identical_copies': None,}

class OffsetSliderForm(ModelForm):
    class Meta:
        model = Lab
        fields = ('offset', )
        widgets = {"offset": RangeInput(attrs={"min": 1, "max": 5, "id": "mySlider"}) }
        help_texts = {
            'offset': None,
        }
