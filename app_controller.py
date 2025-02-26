from aws_s3_files_manager import Files_Manager
from clip_processing import CLIP_Processing_Manager
from gradio_interfaces import Full_AI_Files_Manager_Interface
import os
import pandas as pd

class AppController():
    
    def __init__(self):
        self.app_interface = Full_AI_Files_Manager_Interface()

        self.clip_processing_manager_obj = CLIP_Processing_Manager()

        self.files_manager_obj = Files_Manager()
        self.files_manager_obj.configure_credentials()

    def define_handlers(self, app_interface):
        handlers_dict = {
            'upload_files_handler_func': self.upload_files_handler_func,
            'list_files_handler_func': self.list_files_handler_func,
            'search_files_by_text_prompt_handler_func': self.search_files_by_text_prompt_handler_func,
            'selection_handler_func': self.selection_handler_func
        }

        app_interface.associate_handlers(handlers_dict)

        return app_interface

    def upload_files_handler_func(self, filepaths_list, objects_names_list):
        INDEX_CSV_FILE = 'index.csv'
        LOCAL_INDEX_CSV_PATH = f'./imgs/{INDEX_CSV_FILE}'
        files_list = self.files_manager_obj.list_objects()

        if (INDEX_CSV_FILE in files_list):
            self.files_manager_obj.download_object(INDEX_CSV_FILE, LOCAL_INDEX_CSV_PATH)

        index_metadata = self.clip_processing_manager_obj.get_index_metadata(LOCAL_INDEX_CSV_PATH)
        index_metadata = self.clip_processing_manager_obj.append_new_index_metadata(index_metadata, filepaths_list)
        self.clip_processing_manager_obj.store_index_metadata(index_metadata, LOCAL_INDEX_CSV_PATH)
        
        self.files_manager_obj.upload_file(LOCAL_INDEX_CSV_PATH, INDEX_CSV_FILE)
        for idx, current_file_path_aux in enumerate(filepaths_list):
            print(f'++++ Uploading {current_file_path_aux} to {objects_names_list[idx]}...')
            self.files_manager_obj.upload_file(current_file_path_aux, objects_names_list[idx])

    def list_files_handler_func(self):

        def filter_images(input_value):
            extensions = ['.jpeg', '.jpg', '.png']
            is_image = False
            for extension_aux in extensions:
                is_image = (is_image or (input_value.find(extension_aux)!=-1))

            return is_image

        files_list = self.files_manager_obj.list_objects()

        return files_list
    
    def search_files_by_text_prompt_handler_func(self, text_prompt, image_display):
        if (len(text_prompt.strip())>0):
            INDEX_CSV_FILE = 'index.csv'
            LOCAL_INDEX_CSV_PATH = f'./imgs/{INDEX_CSV_FILE}'
            
            if (not os.path.exists(LOCAL_INDEX_CSV_PATH)):
                self.files_manager_obj.download_object(INDEX_CSV_FILE, LOCAL_INDEX_CSV_PATH)

            index_metadata = self.clip_processing_manager_obj.get_index_metadata(LOCAL_INDEX_CSV_PATH)
            images_names_list = self.clip_processing_manager_obj.search_images_by_text(text_prompt, index_metadata)
        else:
            images_names_list = self.list_files_handler_func()

        return images_names_list

    def selection_handler_func(self, selected_filename):
        local_img_path = f'./imgs/{selected_filename}'

        if (not os.path.exists(local_img_path)):
            print(f'**** Downloading object {selected_filename}...')
            self.files_manager_obj.download_object(selected_filename, local_img_path)
        else:
            print(f'**** {selected_filename} has been already downloaded!')

        return local_img_path

    def run(self):
        self.app_interface.build()
        self.app_interface = self.define_handlers(self.app_interface)
        self.app_interface.run()