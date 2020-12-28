import os
import unittest
from pathlib import Path
from unittest.mock import patch

import sys
sys.path.append(r"D:\coding\Python_codes\Handwriting_extractor_project")

from handwriting.path.path_group import PathGroup
from handwriting.path.signature_dictionary import SignatureDictionary


class TestDictionary(unittest.TestCase):

    @patch("handwriting.signature_dictionary.SignatureDictionaryIterator.current")
    def test_dict_iterator(self, *mocks):
        obj = SignatureDictionary.from_file(Path('../paths_format_transition/anton_test.dict'))
        it = obj.get_iterator()

        for i in range(100):
            print(it.group_iter, it.variant_iter)
            it.prev()


