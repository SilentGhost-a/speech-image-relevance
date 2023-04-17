#!/usr/bin/env python

import argparse
from google.cloud import vision
from google.cloud import speech
from google.cloud import translate_v2 as translate
from google.cloud import language_v1 as language
import six
import os


credential_path = "/Users/fabianbolanos/Library/CloudStorage/OneDrive-UniversidadFidélitas/Paradigmas/Proyecto/gvisionkey.json"
os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credential_path

def detect_labels(file):
    """Detects labels in the file."""
    client = vision.ImageAnnotatorClient()

    # [START vision_python_migration_label_detection]
    # with io.open(path, 'rb') as image_file:
    #     content = image_file.read()

    image = vision.Image(content=file)

    response = client.label_detection(image=image)
    labels = response.label_annotations
    # print('Labels:')

    # for label in labels:
    #     print(label.description)

    label_descriptions = []
    for label in labels:
        label_descriptions.append(label.description.lower())

    return label_descriptions

    # [END vision_python_migration_label_detection]
# def detect_labels_uri(uri):
#     """Detects labels in the file located in Google Cloud Storage or on the
#     Web."""

#     # create ImageAnnotatorClient object
#     client = vision.ImageAnnotatorClient()

#     # create Image object
#     image = vision.Image()

#     # specify location of image
#     image.source.image_uri = uri

#     # get label_detection response by passing image to client
#     response = client.label_detection(image=image)

#     # get label_annotations portion of response
#     labels = response.label_annotations

#     # we only need the label descriptions
#     label_descriptions = []
#     for label in labels:
#         label_descriptions.append(label.description.lower())

#     return label_descriptions


# def transcribe_gcs(language, gcs_uri):
#     """Transcribes the audio file specified by the gcs_uri."""

#     # create ImageAnnotatorClient object
#     client = speech.SpeechClient()

#     # specify location of speech
#     audio = speech.RecognitionAudio(uri=gcs_uri)  # need to specify speech.types

#     # set language to Turkish
#     # removed encoding and sample_rate_hertz
#     config = speech.RecognitionConfig(
#         language_code=language
#     )  # need to specify speech.types

#     # get response by passing config and audio settings to client
#     response = client.recognize(config=config, audio=audio)

#     # naive assumption that audio file is short
#     return response.results[0].alternatives[0].transcript

def transcribe_file(language, alternative_lang, speech_file):
    """Transcribe the given audio file."""
    client = speech.SpeechClient()
    audio = speech.RecognitionAudio(content=speech_file)
    config = speech.RecognitionConfig(
        language_code=language,
        alternative_language_codes=alternative_lang,
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
    print(entities)
    # image -> labels
    labels = detect_labels(image)
    print(labels)
    # naive check for whether entities intersect with labels
    has_match = False
    for entity in entities:
        if entity[:-2] in labels:
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
# if __name__ == "__main__":
#     parser = argparse.ArgumentParser(
#         description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
#     )
#     parser.add_argument("language", help="Language code of speech audio")
#     parser.add_argument("audio", help="GCS path for audio file to be recognised")
#     parser.add_argument("image", help="GCS path for image file to be analysed")
#     args = parser.parse_args()
#     compare_audio_to_image(args.language, args.audio, args.image)
