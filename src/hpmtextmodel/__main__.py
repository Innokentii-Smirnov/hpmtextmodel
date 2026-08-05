from argparse import ArgumentParser
from .corpus import Corpus

if __name__ == '__main__':
  parser = ArgumentParser(
    prog='hpmtextmodel',
    description='Utilities for processing XML files with morphologically annotated texts'
  )
  parser.add_argument('input_directory', help='The directory with corpus XML files')
  subparsers = parser.add_subparsers(dest='subparser_name')
  repl_translit_subparser = subparsers.add_parser('replace_in_transliteration',
    help='Perform a regular expression replacement in transliterations'
  )
  repl_translit_subparser.add_argument('substring_pattern', help='A pattern for the substring to replace')
  repl_translit_subparser.add_argument('replacement', help='The replacement string')
  repl_translit_subparser.add_argument('output_directory',
                                       help='A directory to store modified files')
  repl_translit_subparser.add_argument('--language', choices=['Hit', 'Hur'],
                                       help='The language for which to perform the replacement')
  args = parser.parse_args()
  corpus = Corpus(args.input_directory)
  subparser_args = {key: value for key, value in vars(args).items()
                    if key != 'subparser_name' and key != 'input_directory'}
  getattr(corpus, args.subparser_name)(**subparser_args)
