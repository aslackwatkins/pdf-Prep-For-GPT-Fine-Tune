from classes_and_functions import get_file_names, FileClass, DocData

import constants as cst


pdf_file_name_list = get_file_names()
starting_page = cst.STARTING_PAGE_OF_CONTENT
directory = cst.PDF_DIRECTORY


test_file = pdf_file_name_list[0]
    
doc_data = DocData(test_file, starting_page, directory)

doc_data.get_char_data()

doc_data.get_font_occurances()

doc_data.get_title_fonts()

doc_data.get_titles()

print(doc_data.titles_dict)