from __future__ import annotations
from dataclasses import dataclass
from collections.abc import Iterable
import re
from more_itertools import first
from .selection import Selection
from .morph import Morph, SingleMorph, MultiMorph, Annotation
from re import compile
from bs4 import Tag
from bs4.element import NavigableString
from os.path import exists
from os import remove
from logging import getLogger
logger = getLogger(__name__)

def get_postdet(tag: Tag) -> str | None:
  children = list(tag.children)
  if len(children) > 1:
    postdets = list[str]()
    for child in children[1:]:
      if isinstance(child, Tag) and child.name == 'd':
        postdets.append(child.text)
      elif isinstance(child, NavigableString) and '˽' in child:
        break
    if len(postdets) > 0:
      if len(postdets) > 1:
        logger.error('Ignoring non-first postdeterminatives in %s',
                     tag.decode_contents())
      return first(postdets)
  return None

@dataclass(frozen=True)
class Word:
  transliteration: str
  lang: str
  transcription: str | None
  selections: list[Selection | None]
  analyses: dict[int, str]
  det: str | None
  postdet: str | None
  tag: Tag
  MRP = compile(r'mrp(\d+)')

  @classmethod
  def parse(cls, tag: Tag, default_lang: str) -> Word:
    assert tag.name == 'w'
    transliteration = tag.decode_contents()
    lang = tag.attrs.get('lg', default_lang)
    if not isinstance(lang, str):
      raise ValueError('The attribute lg had a list as a value.')
    if 'trans' in tag.attrs:
      transcription = tag['trans']
      assert isinstance(transcription, str)
    else:
      logger.warning('A word has no transcription attribute: %s.', tag)
      transcription = None
    if 'mrp0sel' in tag.attrs:
      mrp0sel = tag['mrp0sel']
      assert isinstance(mrp0sel, str)
      selections = list(map(Selection.parse, mrp0sel.split()))
    else:
      logger.warning('A word has no selection attribute: %s.', tag)
      selections = []
    analyses = dict[int, str]()
    for attr, value in tag.attrs.items():
      if (match := cls.MRP.fullmatch(attr)) is not None:
        number = int(match.group(1))
        if not isinstance(value, str):
          raise ValueError('The attribute {0} had a list as a value.'.format(attr))
        analyses[number] = value
    children = list(tag.children)
    if (len(children) > 0 and
        isinstance(children[0], Tag) and
        children[0].name == 'd'):
      det = children[0].text
    else:
      det = None
    postdet = get_postdet(tag)
    return Word(transliteration, lang, transcription, selections, analyses, det, postdet, tag)

  def __getitem__(self, number: int) -> Morph | None:
    return Morph.parse(self.analyses[number])

  @property
  def annotations(self) -> list[Annotation]:
    annotations = list[Annotation]()
    for selection in self.selections:
      if selection is not None:
        if selection.lexeme in self.analyses:
          analysis = self.analyses[selection.lexeme]
          morph = Morph.parse(analysis)
          if morph is not None:
            annotation = morph.get_annotation(selection)
            if annotation not in annotations:
              annotations.append(annotation)
    return annotations

  @property
  def all_annotations(self) -> list[Annotation]:
    annotations = list[Annotation]()
    for analysis in self.analyses.values():
      morph = Morph.parse(analysis)
      if morph is not None:
        for morph_tag in morph.to_multi('a').morph_tags.values():
          if morph.enclitics_analysis is None:
            annotation = (morph.segmentation, morph_tag or morph.pos, '_')
            if annotation not in annotations:
              annotations.append(annotation)
          else:
            for encl_tag in morph.enclitics_analysis.to_multi('R').morph_tags.values():
              annotation = (morph.segmentation, morph_tag, encl_tag)
              if annotation not in annotations:
                annotations.append(annotation)
    return annotations

  def is_ambiguous(self) -> bool:
    return len(self.all_annotations) > 1

  def write_analysis(self, index: int) -> None:
    analysis = self.analyses[index]
    self.tag.attrs['mrp' + str(index)] = analysis

  def swap_analyses(self, first_index: int, second_index: int) -> None:
    first_analysis = self.analyses[first_index]
    second_analysis = self.analyses[second_index]
    self.analyses[first_index] = second_analysis
    self.analyses[second_index] = first_analysis
    self.write_analysis(first_index)
    self.write_analysis(second_index)

  def write_selections(self) -> None:
    selections_str = ' '.join(sorted(set(
      map(str, filter(lambda sel: sel is not None, self.selections))
    )))
    self.tag.attrs['mrp0sel'] = selections_str

  def first_analysis_is_selected(self) -> bool:
    for selection in self.selections:
      if selection is not None:
        if selection.lexeme == 1:
          return True
    return False

  def make_first_selected_analysis_first(self) -> None:
    if len(self.analyses) > 1 and not self.first_analysis_is_selected():
      first_selection = first(self.selections)
      if first_selection is not None:
        if first_selection.lexeme != 1:
          self.swap_analyses(first_selection.lexeme, 1)
          first_selection.lexeme = 1
          self.write_selections()

  def normalize_selections(self) -> None:
    for i, selection in enumerate(self.selections):
      if selection is not None:
        if selection.lexeme in self.analyses:
          analysis = self.analyses[selection.lexeme]
          morph = Morph.parse(analysis)
          if morph is not None:
            if isinstance(morph, SingleMorph):
              if selection.gramm_form is not None:
                selection.gramm_form = None
                self.write_selections()
            elif isinstance(morph, MultiMorph) and len(morph.morph_tags) == 1:
              if selection.gramm_form is None:
                selection.gramm_form = first(morph.morph_tags)
                self.write_selections()

  def replace_in_transliteration(self, pattern: re.Pattern[str], replacement: str) -> bool:
    modified = False
    for child in self.tag.children:
      if isinstance(child, NavigableString):
        string = str(child)
        if pattern.search(string) is not None:
          modified = True
          child.replace_with(pattern.sub(replacement, string))
    return modified
