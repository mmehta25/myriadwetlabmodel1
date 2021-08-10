from django.forms import ModelForm, inlineformset_factory, modelformset_factory
from .models import Assay, ProcessInstance, Instrument, InstrumentInstance, Lab, LabAnalysis
from django import forms
from .widgets import RangeInput
import datetime
import pandas as pd

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
class LabAnalysisForm(ModelForm):
    class Meta:
        model= LabAnalysis
        fields = ('failure_rate', )
class LabForm(ModelForm):
    class Meta:
        model= Lab
        fields = ('offset', )

class FailureRateDateRangeForm(forms.Form):
    date = forms.DateField(input_formats=['%Y-%m-%d', ], initial=datetime.date.today, help_text="Pick end date for 3 month date range. Default is todays date.")
    def clean_date(self):
        data = self.cleaned_data['date']

        # Check if a date is not in the past.
        if data > datetime.date.today():
            raise ValidationError(_('Invalid date - date in future'))
        # Remember to always return the cleaned data.
        return data

df_an = pd.read_csv('~/django_projects/myriadwetlab/labmodel/data/instruments.csv')
df_an = df_an.set_index('Instrument type')
df_an = df_an['Asset numbers'].to_dict()

inst_choices = []
for key in df_an:
    inst_choices.append((df_an[key], key))
  
# creating a form 
class OffsetForm(forms.Form):
    Instrument = forms.ChoiceField(choices = tuple(inst_choices), help_text="Pick an instrument type to view all data on all of its instances.")
