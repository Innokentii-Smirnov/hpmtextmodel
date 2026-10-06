from __future__ import annotations
from dataclasses import dataclass
import re
from logging import getLogger
logger = getLogger(__name__)

@dataclass(order=True)
class Selection:
    lexeme: int
    gramm_form: str | None
    encl_chain: str | None
    selection_pattern = re.compile(r'(\d+)([a-z]+)?([A-Z]+)?')
    sep = '.'

    def get_elements(self) -> tuple[int, str | None, str | None]:
        return self.lexeme, self.gramm_form, self.encl_chain

    @classmethod
    def from_strings(cls, lexeme: str, gramm_form: str | None, encl_chain: str | None) -> Selection:
        return cls(int(lexeme), gramm_form, encl_chain)

    @classmethod
    def parse(cls, selection: str) -> Selection | None:
        matched = cls.selection_pattern.fullmatch(selection)
        if selection == 'DEL' or selection == 'HURR':
          logger.info('Uninformative selection: %s.', selection)
          return None
        if selection.startswith('DEL') or selection.startswith('HURR'):
          logger.error('Incorrect selection: %s.', selection)
          return None
        if matched is not None:
            lexeme, gramm_form, encl_chain = matched.groups()
            return cls.from_strings(lexeme, gramm_form, encl_chain)
        else:
            logger.error('Cannot parse selection: %s.', selection)
            return None
    
    def __str__(self) -> str:
        string = str(self.lexeme)
        if self.gramm_form is not None:
            string += self.gramm_form
        if self.encl_chain is not None:
            string += self.encl_chain
        return string
