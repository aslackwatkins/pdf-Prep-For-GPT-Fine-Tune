import json
import codecs

from classes_and_functions import get_file_names, DocData

import constants as cst


pdf_file_name_list = get_file_names()
starting_page = cst.STARTING_PAGE_OF_CONTENT
directory = cst.PDF_DIRECTORY
org_name = cst.NAME_OF_ORG


for name in pdf_file_name_list:
    
    doc_data = DocData(name, starting_page, directory)

    doc_data.get_char_data()

    doc_data.get_font_occurances()

    doc_data.get_title_fonts()

    doc_data.get_titles()

    doc_data.get_tolerances()

    doc_data.get_text()

    doc_data.clean_text()

    current_doc_content = doc_data.return_text()

    prepared_dictionaries = []

    #prepare the dictionaries for json with prompts conditional to title existing

    for item in current_doc_content:
        current_dictionary = {"prompt": "", "completion": ""}
        
        if len(item[0]) < 4:
            current_dictionary["prompt"] += f"What did {org_name} give as their policy position in their {name} document?"
        
        else:
            current_dictionary["prompt"] += f"What did {org_name} give as their policy position on {item[0]} in their {name} document?"

        current_dictionary["completion"] += item[1]

        prepared_dictionaries.append(current_dictionary)

    with open("training_data.JSONL", "a") as json_file:
        line_number = 1

        for item in prepared_dictionaries:
            json_object = json.dumps(item)

            if line_number == 1:
                json_file.write(json_object)
                line_number += 1

            else:
                json_file.write("\n")
                json_file.write(json_object)
                line_number += 1

#To-Do's
    #Still can't figure out how to remove the unicode characters
    #Currently trying to write them to a text file then replace them with nothing, but that isn't working
    #i think because every time python grabs it as a string it becomes unicode again
    #i need to grab it when it's still text and replace it