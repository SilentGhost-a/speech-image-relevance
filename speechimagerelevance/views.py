from django.shortcuts import render
from django.http import HttpResponse
from .forms import FileUploadForm
from .google_ai import compare_audio_to_image, translate_audio
from django.http import JsonResponse

def compare(request):
    image_file = request.FILES['image_file'].file.getvalue()
    audio_file = request.FILES['audio_file'].file.getvalue()
    # audio_file = form.cleaned_data["audio"]
        
    response = compare_audio_to_image('tr-TR',['de-DE', 'en-US'],audio_file,image_file)
    print (response)
    return JsonResponse({'message': response})
    # return render(request, "compare.html", {"form": form})

def translate(request):
    # get the uploaded audio file name from the request
    audio_file = request.FILES['audio_file'].file.getvalue()
    response = translate_audio('tr-TR', ['de-DE', 'en-US'],audio_file)
    print (response)
    return JsonResponse({'message': response})


def index(request):
    return render(request, 'compare.html')