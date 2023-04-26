import os
import pdfplumber
import string
import pandas as pd
import numpy as np

from statistics import stdev, mean




def get_file_names():
    working_dir = os.getcwd()
    directory_string = f"{working_dir}/pdf_data"
    directory = os.fsencode(directory_string)

    list_of_files = []

    for file in os.listdir(directory):
        list_of_files.append(os.fsdecode(file))
    return list_of_files



class DocData():
    
    def __init__(self,file_name,starting_page,pdf_directory,csv_directory):
        self.file_name = file_name
        self.pdf_directory = pdf_directory
        self.pdf = pdfplumber.open(self.pdf_directory + "/" + self.file_name)
        self.starting_page = starting_page
        self.doc_length = len(self.pdf.pages)
        self.metadata = self.pdf.metadata
        self.csv_directory = csv_directory

        self.title_size = []
        self.font_dict_sizes = {}
        self.font_dict_occurances = {}
        self.titles_dict = {}

        self.y_tolerance_list = []
        self.x_tolerance_list = []
        self.page_list = []
        self.font_list = []
        self.size_list = []
        self.text_list = []
        self.adv_list = []
        self.y0_list = []
        self.y1_list = []
        self.x0_list = []
        self.x1_list = []
        self.matrix_list = []
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
                    self.y_tolerance_list.append(0.0)
                    self.x_tolerance_list.append(0.0)
                    self.page_list.append(item['page_number'])
                    self.font_list.append(item['fontname'])
                    self.size_list.append(item['size'])
                    self.text_list.append(item['text'])
                    self.adv_list.append(item['adv'])
                    self.y0_list.append(item['y0'])
                    self.x0_list.append(item['x0'])
                    self.y1_list.append(item['y1'])
                    self.x1_list.append(item['x1'])
                    self.matrix_list.append(item['matrix'])

                else:
                    self.y_tolerance_list.append(abs(item['doctop'] - last_doctop))
                    self.x_tolerance_list.append(abs(item['x0'] - last_x1))
                    self.page_list.append(item['page_number'])
                    self.font_list.append(item['fontname'])
                    self.size_list.append(item['size'])
                    self.text_list.append(item['text'])
                    self.adv_list.append(item['adv'])
                    self.y0_list.append(item['y0'])
                    self.x0_list.append(item['x0'])
                    self.y1_list.append(item['y1'])
                    self.x1_list.append(item['x1'])
                    self.matrix_list.append(item['matrix'])

    def to_csv(self):
        new_dataframe = pd.DataFrame({'page_number': self.page_list, 
                                      'y_diff': self.y_tolerance_list, 
                                      'x_diff': self.x_tolerance_list,
                                      'fontname': self.font_list,
                                      'size': self.size_list,
                                      'text': self.text_list,
                                      'adv': self.adv_list,
                                      'y0': self.y0_list,
                                      'y1': self.y1_list,
                                      'x0': self.x0_list,
                                      'x1': self.x1_list,
                                      'matrix': self.matrix_list})
        
        new_dataframe.to_csv(f'{self.csv_directory}{self.file_name}pdf_data.csv')

    def get_font_occurances(self):

        for num in range(self.starting_page,self.doc_length):
            current_page = self.pdf.pages[num].chars

            for item in current_page:
                if item['fontname'] in self.font_dict_occurances and num not in self.font_dict_occurances[item['fontname']]:
                    self.font_dict_occurances[item['fontname']].append(num)
                
                elif item['fontname'] not in self.font_dict_occurances:
                    self.font_dict_occurances[item['fontname']] = [num]
    

    def get_title_fonts(self):

        #sorted large to small
        font_sizes = set(self.font_dict_sizes.values())
        font_sizes_sorted = list((sorted(font_sizes)))

        print(font_sizes_sorted)

        array = np.array(font_sizes_sorted)
        quantile = np.quantile(a=array, q=0.75)

        if array.size < 4:
            self.title_size.append(array[-1])
            print(f"Less than 4: {self.file_name}")

        else:
            for size in array:
                if size > quantile:
                    self.title_size.append(size)

                    print(f"Greater than 4 {self.file_name}")


    def get_titles(self):

        for num in range(self.starting_page, self.doc_length):
            current_page = self.pdf.pages[num].chars

            for item in current_page:
                if item['size'] in self.title_size:

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

                if (x - x_lists[-1][-1]) / x_stdev > 0.5:
                    x_lists.append([])

                x_lists[-1].append(x)
        else:
            x_lists = [[0.0]]
        
        self.x_tolerance = x_lists[0][-1]

        if len(y_gaps) > 1 and mean(y_gaps) != 0:
            y_stdev = stdev(y_gaps)
            y_lists = [[y_sorted_data[0]]]

            for y in y_sorted_data[1:]:

                if (y - y_lists[-1][-1]) / y_stdev > 0.5:
                    y_lists.append([])

                y_lists[-1].append(y)
        else:
            y_lists = [[0.0]]
        
        self.y_tolerance = y_lists[0][-1]


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

        title_keys_list = [key for key in self.titles_dict.keys()]
        text_keys_list = [key for key in self.text_dict.keys()]

        with open(f"{self.file_name}_titles.txt", "a") as titles_txt:
            line_number = 1
            for key in title_keys_list:
                if line_number == 1:
                    current_text = self.titles_dict[key].encode(encoding='ascii', errors='ignore')
                    titles_txt.write(current_text.decode())
                    line_number += 1
                
                else:
                    current_text = self.titles_dict[key].encode(encoding='ascii', errors='ignore')
                    titles_txt.write("\n")
                    titles_txt.write(current_text.decode())
                    line_number += 1

        with open(f"{self.file_name}_text.txt", "a") as text_txt:
            line_number = 1
            for key in text_keys_list:
                if line_number == 1:
                    current_text = self.text_dict[key].encode(encoding='ascii', errors='ignore')
                    print(current_text)
                    text_txt.write(current_text.decode())
                    line_number += 1
                
                else:
                    current_text = self.text_dict[key].encode(encoding='ascii', errors='ignore')
                    text_txt.write("\n")
                    text_txt.write(current_text.decode())
                    line_number += 1

        with open(f"{self.file_name}_titles.txt", "r") as titles_txt:
            title_num = 0

            for title in titles_txt:
                current_string = title.replace('\n', '')
                printable = set(string.printable)
                self.titles_dict[title_keys_list[title_num]] = ''.join(filter(lambda x: x in printable, current_string))
                title_num += 1

        with open(f"{self.file_name}_text.txt", "r") as text_txt:
            text_num = 0

            for text in text_txt:
                current_string = text.replace('\n','')
                printable = set(string.printable)
                self.text_dict[text_keys_list[text_num]] = ''.join(filter(lambda x: x in printable, current_string))

        


    def return_text(self):
        packaged = []

        for num in range(self.starting_page, self.doc_length):
            
            title_key_list = self.titles_dict.keys()
            current_package = []
            current_title = ""

            for i in title_key_list:
                if i <= num:
                    current_title = self.titles_dict[i]

            current_package.append(current_title)
            current_package.append(self.text_dict[num])

            packaged.append(current_package)

        return packaged
            

            

            



