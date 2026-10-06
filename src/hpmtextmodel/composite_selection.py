from dataclasses import dataclass
from .selection import Selection

@dataclass
class CompositeSelection:
  wordform_selections: list[WordformSelection]

  def __init__(self, length: int) -> None:
    self.wordform_selections = [WordformSelection() for _ in range(length)]

  def __getitem__(self, index: int) -> WordformSelection:
    return self.wordform_selections[index]

  @property
  def non_empty_wordform_selections(self) -> list[WordformSelection]:
    return list(filter(
      lambda wordform_selection: not wordform_selection.is_empty(),
      self.wordform_selections
    ))

  def is_empty(self) -> bool:
    return len(self.non_empty_wordform_selections) == 0

  def __str__(self) -> str:
    return '+'.join(map(str, self.non_empty_wordform_selections))

@dataclass
class WordformSelection:
  selections: list[Selection]

  def __init__(self) -> None:
    self.selections = list()

  def append(self, selection: Selection) -> None:
    self.selections.append(selection)

  def is_empty(self) -> bool:
    return len(self.selections) == 0

  def __str__(self) -> str:
    self.selections.sort()
    joined_selections = ','.join(map(str, self.selections))
    if len(self.selections) <= 1:
      return joined_selections
    return '{' + joined_selections + '}'
