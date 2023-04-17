from django import forms

class FileUploadForm(forms.Form):
    image = forms.ImageField()
    audio = forms.FileField()