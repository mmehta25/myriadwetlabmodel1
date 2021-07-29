from django.forms.widgets import NumberInput, DateInput


class RangeInput(NumberInput):
    input_type = "range"

class SelectDateWidget(DateInput):
	input_type = "range"
