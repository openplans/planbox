from django import forms

class FilterForm (forms.Form):
    datetime_field = forms.CharField()
