from __future__ import annotations
from dataclasses import dataclass
from collections.abc import Iterable
from typing import Callable, Sequence, Optional
import regex as re
from bs4 import Tag
from .text import Text, SentenceBoundary
import os
from tqdm.auto import tqdm
from os import path
from .line import Line
from itertools import chain
from logging import getLogger
from .word import Word
from .morph import Annotation
logger = getLogger(__name__)

PROCESSED_FILE_LOGGER_NAME = 'processed_files'
processed_file_logger = getLogger(PROCESSED_FILE_LOGGER_NAME)
SKIPPED_FILE_LOGGER_NAME = 'skipped_files'
skipped_file_logger = getLogger(SKIPPED_FILE_LOGGER_NAME)

def to_be_procecced(triple: tuple[str, list[str], list[str]]) -> bool:
  dirpath, dirnames, filenames = triple
  _, folder = path.split(dirpath)
  return folder != 'Backup'

@dataclass
class Corpus:
  input_directory: str

  def sentences(self, sentence_boundaries: Sequence[SentenceBoundary],
                on_text_end: Callable[[Text], None]) -> Iterable[Iterable[tuple[Tag, str]]]:
    for text in self.texts:
      for sentence in text.sentences(sentence_boundaries):
        yield sentence
      on_text_end(text)

  @property
  def texts(self) -> Iterable[Text]:
    walk = sorted(filter(to_be_procecced, os.walk(self.input_directory)))
    progress_bar = tqdm(walk)
    for dirpath, dirnames, filenames in progress_bar:
      rel_path = dirpath.removeprefix(self.input_directory).removeprefix(os.sep)
      processed_file_logger.info(rel_path)
      _, folder = path.split(dirpath)
      progress_bar.set_postfix_str(folder)
      for filename in sorted(filenames):
        text_id, ext = path.splitext(filename)
        if ext == '.xml':
          rel_name = path.join(rel_path, filename)
          infile = path.join(dirpath, filename)
          try:
            with open(infile, 'r', encoding='utf-8') as fin:
              text = Text.parse(rel_path, text_id, fin)
            if text is None:
              skipped_file_logger.info(rel_name)
            else:
              yield text
          except (KeyError, ValueError, AssertionError):
            skipped_file_logger.info(rel_name)
            logger.exception(
              'A text could not be read from the file %s because of the following exception:', rel_name
            )

  @property
  def words(self) -> Iterable[Word]:
    return chain.from_iterable(text.words for text in self.texts)

  def iterate_over_words(self, on_text_end: Callable[[Text], None]) -> Iterable[Word]:
    for text in self.texts:
      yield from text.words
      on_text_end(text)

  @property
  def annotations(self) -> Iterable[list[Annotation]]:
    for text in self.texts:
      yield from text.annotations

  def zip(self, other: Corpus) -> Iterable[tuple[Text, Text]]:
    for own_text, other_text in zip(self.texts, other.texts, strict=True):
      if own_text.text_id != other_text.text_id:
        message = 'Texts had different identifiers: {0} and {1}'.format(
          own_text.text_id, other_text.text_id
        )
        raise ValueError(message)
      yield own_text, other_text

  def replace_in_transliteration(self, substring_pattern: str, replacement: str,
                                 output_directory: str, language: Optional[str] = None) -> None:
    pattern = re.compile(substring_pattern)
    for text in self.texts:
      modified = False
      for word in text.words:
        if language is None or word.lang == language:
          word_modified = word.replace_in_transliteration(pattern, replacement)
          modified = modified or word_modified
      if modified:
        text.store_in(output_directory)
