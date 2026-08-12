from argparse import ArgumentParser
from .corpus import Corpus

SUBPARSER_ARGUMENT_NAME = 'subparser_name'
OUTPUT_DIRECTORY_ARGUMENT_NAME = 'output_directory'
MAIN_PARSER_ARGS = {
  SUBPARSER_ARGUMENT_NAME,
  'input_directory',
  'inplace'
}

if __name__ == '__main__':
  parser = ArgumentParser(
    prog='hpmtextmodel',
    description='Utilities for processing XML files with morphologically annotated texts'
  )
  parser.add_argument('input_directory', help='The directory with corpus XML files')
  parser.add_argument('--inplace', action='store_true', help='Modify the texts in place')
  subparsers = parser.add_subparsers(dest=SUBPARSER_ARGUMENT_NAME)
  repl_translit_subparser = subparsers.add_parser('replace_in_transliteration',
    help='Perform a regular expression replacement in transliterations'
  )
  repl_translit_subparser.add_argument('substring_pattern', help='A pattern for the substring to replace')
  repl_translit_subparser.add_argument('replacement', help='The replacement string')
  repl_translit_subparser.add_argument('--' + OUTPUT_DIRECTORY_ARGUMENT_NAME,
                                       help='A directory to store modified files')
  repl_translit_subparser.add_argument('--language', choices=['Hit', 'Hur'],
                                       help='The language for which to perform the replacement')
  norm_brack_parser = subparsers.add_parser('normalize_brackets',
    help='Ensure zero bracket balance at word boundaries.'
  )
  norm_brack_parser.add_argument('bracket_type', choices=['del', 'laes', 'ras'],
                                 help='The type of brackets to normalize')
  norm_brack_parser.add_argument('--' + OUTPUT_DIRECTORY_ARGUMENT_NAME,
                                 help='A directory to store modified files')
  args = parser.parse_args()
  corpus = Corpus(args.input_directory)
  subparser_args = {key: value for key, value in vars(args).items()
                    if key not in MAIN_PARSER_ARGS}
  if args.inplace:
    subparser_args[OUTPUT_DIRECTORY_ARGUMENT_NAME] = args.input_directory
  getattr(corpus, args.subparser_name)(**subparser_args)
