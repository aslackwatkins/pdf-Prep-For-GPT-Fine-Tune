import os
import math
import pdfplumber

from statistics import stdev, mean




def get_file_names():
    working_dir = os.getcwd()
    directory_string = f"{working_dir}/pdf_data"
    directory = os.fsencode(directory_string)

    list_of_files = []

    for file in os.listdir(directory):
        list_of_files.append(os.fsdecode(file))
    return list_of_files



class FileClass():

    def __init__(self, file_name, file_type):
        self.file_name = file_name
        self.file_type = file_type

    def write(self,text):

        with open(f"{self.file_name}+{self.file_type}", "a") as file:
            file.write(text)
        file.close()

    def read(self,starting_line,exclusive_end):
        with open(f"{self.file_name}+{self.file_type}", "r") as file:
            file.read()[starting_line,exclusive_end]
        file.close()



class DocData():
    
    def __init__(self,file_name,starting_page,pdf_directory):
        self.file_name = file_name
        self.pdf_directory = pdf_directory
        self.pdf = pdfplumber.open(self.pdf_directory + "/" + self.file_name)
        self.starting_page = starting_page
        self.doc_length = len(self.pdf.pages)
        self.metadata = self.pdf.metadata

        self.title_font = []
        self.font_dict_sizes = {}
        self.font_dict_occurances = {}
        self.titles_dict = {}

        self.y_tolerance_list = []
        self.x_tolerance_list = []
        self.y_tolerance = 0
        self.x_tolerance = 0
        self.text_dict = {}


    def get_char_data(self):
        
        for num in range(self.starting_page,self.doc_length):
            current_page = self.pdf.pages[num].chars

            last_x1 = 0.0
            last_doctop = 0.0

            for item in current_page:
                
                if item['fontname'] not in self.font_dict_sizes:
                    self.font_dict_sizes[item['fontname']] = round(item['size'])

                if last_x1 == 0.0 or last_doctop == 0.0:
                    last_x1 = item['x1']
                    last_doctop = item['doctop']

                else:
                    self.y_tolerance_list.append(abs(item['doctop'] - last_doctop))
                    self.x_tolerance_list.append(abs(item['x0'] - last_x1))


    def get_font_occurances(self):

        for num in range(self.starting_page,self.doc_length):
            current_page = self.pdf.pages[num].chars

            for item in current_page:
                if item['fontname'] in self.font_dict_occurances and num not in self.font_dict_occurances[item['fontname']]:
                    self.font_dict_occurances[item['fontname']].append(num)
                
                elif item['fontname'] not in self.font_dict_occurances:
                    self.font_dict_occurances[item['fontname']] = [num]
    

    def get_title_fonts(self):
        
        font_keys_sorted = []

        #sorted large to small
        font_sizes = set(self.font_dict_sizes.values())
        font_sizes_sorted = list(reversed(sorted(font_sizes)))


        for value in font_sizes_sorted:
            sorted_key = [i for i in self.font_dict_sizes if self.font_dict_sizes[i] == value]
            font_keys_sorted.extend(sorted_key)

        title_approved = []

        for title_key in font_keys_sorted:
            if len(self.font_dict_occurances[title_key]) >= (self.doc_length / 10):
                title_approved.append(True)

        font_size_occurance_count = 0

        for num in range(0, len(title_approved)):
            if title_approved[num] == True:
                current_size = font_sizes_sorted[num]
                current_fonts = [i for i in self.font_dict_sizes if self.font_dict_sizes[i] == current_size]

                font_size_occurance_count = len(current_fonts)

                if font_size_occurance_count == 1:
                    self.title_font.append(font_keys_sorted[num])
                    break
                
                else:
                    occurances = []

                    for o in range(0, font_size_occurance_count):
                        occurances.append(len(self.font_dict_occurances[font_keys_sorted[o]]))

                    index = occurances.index(max(occurances))

                    self.title_font.append(font_keys_sorted[index])
                    break


    def get_titles(self):

        for num in range(self.starting_page, self.doc_length):
            current_page = self.pdf.pages[num].chars

            for item in current_page:
                if item['fontname'] in self.title_font:

                    if item['page_number'] in self.titles_dict:
                        self.titles_dict[item['page_number']] += item['text']

                    else:
                        self.titles_dict[item['page_number']] = ''

                        self.titles_dict[item['page_number']] += item['text']
    

    def get_tolerances(self):
        
        x_sorted_data = sorted(self.x_tolerance_list)
        x_gaps = [y - x for x, y in zip(x_sorted_data[:-1], x_sorted_data[1:])]
        x_lists = []
        y_sorted_data = sorted(self.y_tolerance_list)
        y_gaps = [y - x for x, y in zip(y_sorted_data[:-1], y_sorted_data[1:])]
        y_lists = []

        if len(x_gaps) > 1:
            x_stdev = stdev(x_gaps)  
            x_lists = [[x_sorted_data[0]]]

            for x in x_sorted_data[1:]:

                if (x - x_lists[-1][-1]) / x_stdev > 1:
                    x_lists.append([])

                x_lists[-1].append(x)
        else:
            x_lists = [[0.0]]
        
        self.x_tolerance = x_lists[0][0]

        if len(y_gaps) > 1 and mean(y_gaps) != 0:
            y_stdev = stdev(y_gaps)
            y_lists = [[y_sorted_data[0]]]

            for y in y_sorted_data[1:]:

                if (y - y_lists[-1][-1]) / y_stdev > 1:
                    y_lists.append([])

                y_lists[-1].append(y)
        else:
            y_lists = [[0.0]]
        
        self.y_tolerance = y_lists[0][0]


    def get_text(self):

        for num in range(self.starting_page, self.doc_length):
            current_page = self.pdf.pages[num]

            
            
            word_list = current_page.extract_words(x_tolerance = self.x_tolerance, 
                                                            y_tolerance = self.y_tolerance, 
                                                            keep_blank_chars = True,
                                                            use_text_flow = True,
                                                            expand_ligatures = True)
            
            self.text_dict[num] = ''

            for word in word_list:

                self.text_dict[num] += word['text']


    def clean_text(self):

        for num in range(self.starting_page, self.doc_length):
            self.text_dict[num].replace("", "")