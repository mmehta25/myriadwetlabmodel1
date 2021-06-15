from django.forms import ModelForm, inlineformset_factory, modelformset_factory
from .models import Assay, ProcessInstance, InstrumentInstance


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
      fields = ['instrument', 'processinstance', 'integrated_or_walkup']

InstrumentInstanceFormSet = modelformset_factory(
    InstrumentInstance, fields=("instrument", "processinstance", 'integrated_or_walkup'), extra=1
)