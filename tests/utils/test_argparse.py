from zernikegrams.utils.argparse import *

def test_comma_sep_list_of_int_or_float_or_bool():
    assert comma_sep_list_of_int_or_float_or_bool('[.1, .9, False]') == [.1, .9, False]