from typing import Literal

type BracketType = Literal['laes', 'del', 'ras']
OPENING_BRACKET_SUFFIX = '_in'
CLOSING_BRACKET_SUFFIX = '_fin'

def get_opening_bracket(bracket_type: BracketType) -> str:
  return bracket_type + OPENING_BRACKET_SUFFIX

def get_closing_bracket(bracket_type: BracketType) -> str:
  return bracket_type + CLOSING_BRACKET_SUFFIX
