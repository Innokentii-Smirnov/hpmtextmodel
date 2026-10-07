import re

def removeMacron(s: str) -> str:
  return s \
    .replace('ā', 'a') \
    .replace('ē', 'e') \
    .replace('ī', 'i') \
    .replace('ō', 'o') \
    .replace('ū', 'u') \
    .replace('Ā', 'A') \
    .replace('Ē', 'E') \
    .replace('Ī', 'I') \
    .replace('Ō', 'O') \
    .replace('Ū', 'U')

def convertLabialFricativesToStops(word: str) -> str:
  return word.replace('f', 'p').replace('v', 'b')

def convertMidVowelsToHigh(word: str) -> str:
  return word.replace('e', 'i').replace('o', 'u')

def convertVoicedConsonantsToVoiceless(word: str) -> str:
  return word.replace('b', 'p') \
             .replace('d', 't') \
             .replace('g', 'k') \
             .replace('v', 'f') \
             .replace('z', 's') \
             .replace('ž', 'š') \
             .replace('ġ', 'ḫ')

VOWEL_BEFORE_VOWEL = re.compile(r'[aeiou](?=[+-=][aeiou])')
def remove_vowel_before_vowel(word: str) -> str:
  return VOWEL_BEFORE_VOWEL.sub('', word)

def generalize_transcription(word: str) -> str:
  word = convertLabialFricativesToStops(word)
  word = convertMidVowelsToHigh(word)
  word = convertVoicedConsonantsToVoiceless(word)
  return word

def preprocess_transcription(transcription: str) -> str:
  transcription = removeMacron(transcription)
  transcription = generalize_transcription(transcription)
  return transcription

def preprocess_segmentation(segmentation: str) -> str:
  segmentation = generalize_transcription(segmentation)
  segmentation = remove_vowel_before_vowel(segmentation)
  return segmentation
