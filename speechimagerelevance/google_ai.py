#!/usr/bin/env python

import argparse
from google.cloud import vision
from google.cloud import speech
from google.cloud import translate_v2 as translate
from google.cloud import language_v1 as language
import six
import os
from pattern.text.en import singularize

credential_path = "/Users/fabianbolanos/Library/CloudStorage/OneDrive-UniversidadFidélitas/Paradigmas/Proyecto/gvisionkey.json"
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path

def detect_labels(file):
    """Detects labels in the file."""
    client = vision.ImageAnnotatorClient()


    image = vision.Image(content=file)

    response = client.label_detection(image=image)
    labels = response.label_annotations

    label_descriptions = []
    for label in labels:
        label_descriptions.append(label.description.lower())

    return label_descriptions

    # [END vision_python_migration_label_detection]

def transcribe_file(language, alternative_lang, speech_file):
    """Transcribe the given audio file."""
    client = speech.SpeechClient()
    audio = speech.RecognitionAudio(content=speech_file)
    config = speech.RecognitionConfig(
        language_code=language,
        alternative_language_codes=alternative_lang,
        audio_channel_count = 1
    )

    response = client.recognize(config=config, audio=audio)
    return response.results[0].alternatives[0].transcript

def translate_text(target, text):
    """Translates text into the target language.
    Target must be an ISO 639-1 language code.
    See https://g.co/cloud/translate/v2/translate-reference#supported_languages
    """

    # create Client object
    translate_client = translate.Client()

    # decode text if it's a binary type
    if isinstance(text, six.binary_type):
        text = text.decode("utf-8")

    # get translation result by passing text and target language to client
    # Text can also be a sequence of strings, in which case this method
    # will return a sequence of results for each text.
    result = translate_client.translate(text, target_language=target)

    # only interested in translated text
    return result["translatedText"]


def entities_text(text):
    """Detects entities in the text."""

    # create LanguageServiceClient object
    client = language.LanguageServiceClient()

    # decode text if it's a binary type
    if isinstance(text, six.binary_type):
        text = text.decode("utf-8")

    # Instantiates a plain text document.
    # need to specify language.types
    document = language.types.Document(
        content=text, type=language.Document.Type.PLAIN_TEXT
    )

    # Detects entities in the document. You can also analyze HTML with:
    #   document.type == enums.Document.Type.HTML
    entities = client.analyze_entities(request={"document": document}).entities

    # we only need the entity names
    entity_names = []
    for entity in entities:
        entity_names.append(entity.name)
    return entity_names

def compare_audio_to_image(language, alternative_lang, audio, image):
    """Checks whether a speech audio is relevant to an image."""
    # speech audio -> text
    transcription = transcribe_file(language, alternative_lang, audio)
    print(transcription)
    # text of any language -> english text
    translation = translate_text("en", transcription)
    print(translation)
    # text -> entities
    entities = entities_text(translation)
    entities_singular = [singularize(entity) for entity in entities]
    print(entities_singular)
    # image -> labels
    labels = detect_labels(image)
    print(labels)
    # naive check for whether entities intersect with labels
    has_match = False
    for entity in entities_singular:
        if entity in labels:
            print("The audio and image both contain: {}".format(entity))
            has_match = True
            message = 'The audio and image match!'
    if not has_match:
        print("The audio and image do not appear to be related.")
        message = 'The audio and image do not match.'
    return message

def translate_audio(language, alternative_lang, audio):
    transcription = transcribe_file(language, alternative_lang, audio)
    translation = translate_text("es", transcription)
    return translation