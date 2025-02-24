from gradio_interfaces import Full_AI_Files_Manager_Interface
from aws_s3_files_manager import Files_Manager
import os

class AppController():
    
    def __init__(self):
        self.app_interface = Full_AI_Files_Manager_Interface()

        self.files_manager_obj = Files_Manager()
        self.files_manager_obj.configure_credentials()

    def define_handlers(self, app_interface):
        handlers_dict = {
            'upload_files_handler_func': self.upload_files_handler_func,
            'list_files_handler_func': self.list_files_handler_func,
            'selection_handler_func': self.selection_handler_func
        }

        app_interface.associate_handlers(handlers_dict)

        return app_interface

    def upload_files_handler_func(self, file_path, object_name):
        self.files_manager_obj.upload_file(file_path, object_name)

    def list_files_handler_func(self):
        files_list = self.files_manager_obj.list_objects()

        return files_list
    
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

def main():
    app_controller = AppController()
    app_controller.run()

main()