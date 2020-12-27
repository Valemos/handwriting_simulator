from handwriting.page_writing.page import Page
from handwriting.path_management.signature_dictionary import SignatureDictionary


class HandwrittenTextWriter:
    def __init__(self, page, dictionary):
        self.page: Page = page
        self.dictionary: SignatureDictionary = dictionary

    def write_text(self, test_text):
        return self.dictionary[test_text[0]][0]


