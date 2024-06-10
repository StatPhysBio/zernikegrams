from zernikegrams.utils.argparse import *

def test_comma_sep_list_of_int_or_float_or_bool():
    assert comma_sep_list_of_int_or_float_or_bool('[.1, .9, False]') == [.1, .9, False]

def test_ast_parse():
    assert ast_parse('[.1, .9, False]') == [.1, .9, False]
    assert ast_parse('[.1, .9, False, (2, 1, 4)]',) == [.1, .9, False, (2, 1, 4)]