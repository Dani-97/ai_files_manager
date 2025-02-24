import configparser
import gradio as gr
import os
from PIL import Image

class UniversalFactory():

    def __init__(self):
        pass

    def create_object(self, namespace, classname, kwargs):
        ClassName = namespace[classname]
        universal_obj = ClassName(**kwargs)

        return universal_obj

# This is an abstract class.
class Base_Interface():

    def __init__(self):
        pass

    def associate_handlers(self, handlers):
        self.handlers = handlers

    def get_app_obj(self):
        pass

    def build(self):
        pass

    def run(self):
        pass

class Full_AI_Files_Manager_Interface(Base_Interface):
    
    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('config.cfg')

        # self.sub_interfaces_list = ['Upload_Files_Interface', 
        #                             'Search_Files_Interface', 
        #                             'Delete_Files_Interface']
        self.sub_interfaces_list = ['Upload_Files_Interface', 
                                    'Search_Files_Interface']
        self.tabs_names_list = list(map(lambda input_value: input_value.split('_')[0], self.sub_interfaces_list))

    def associate_handlers(self, handlers):
        for sub_interface_app_obj_aux in self.subinterfaces_objs_list:
            sub_interface_app_obj_aux.associate_handlers(handlers)

    def build(self):
        universal_factory_obj = UniversalFactory()

        self.subinterfaces_objs_list = []
        self.app_objs_list = []
        for sub_interface_aux in self.sub_interfaces_list:
            kwargs = {}
            current_subinterface_obj = universal_factory_obj.create_object(globals(), sub_interface_aux, kwargs)
            current_subinterface_obj.build()
            self.subinterfaces_objs_list.append(current_subinterface_obj)
            self.app_objs_list.append(current_subinterface_obj.get_app_obj())

        self.full_app = gr.TabbedInterface(self.app_objs_list, self.tabs_names_list)

    def run(self):
        HOST_IP_ADDRESS = self.config['SERVER']['HOST_IP_ADDRESS']
        PORT_NUMBER = int(self.config['SERVER']['PORT_NUMBER'])

        self.full_app.launch(server_name=HOST_IP_ADDRESS, server_port=PORT_NUMBER)

class Upload_Files_Interface(Base_Interface):

    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('config.cfg')

    def get_app_obj(self):
        return self.app_obj

    def upload_files_handler_func(self, filepaths_list):
        filenames_list = list(map(lambda input_value: os.path.basename(input_value), filepaths_list))
        for idx, current_filename_aux in enumerate(filenames_list):        
            self.handlers['upload_files_handler_func'](filepaths_list[idx], current_filename_aux) 

        new_filenames_list_df = self.handlers['list_files_handler_func']()

        return new_filenames_list_df

    def build(self):
        with gr.Blocks() as self.app_obj:
            file_upload_slot = gr.File(file_count="multiple")
            upload_button = gr.Button('Upload')

            files_list = gr.Dataframe(
                headers=['Files names'],
                interactive=False,
                type='array'
            )

            upload_button.click(
                self.upload_files_handler_func,
                file_upload_slot,
                files_list
            )

class Search_Files_Interface(Base_Interface):

    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('config.cfg')

    def list_files_handler_func(self, empty_df):
        files_list_output_df = self.handlers['list_files_handler_func']()

        return files_list_output_df

    def selection_handler_func(self, files_list, evt: gr.SelectData):
        selected_filename = files_list[evt.index[0]][evt.index[1]]
        local_img_path = self.handlers['selection_handler_func'](selected_filename)

        pil_image = Image.open(local_img_path)
        image_shape = pil_image.size
        image_width, image_height = image_shape[0], image_shape[1]
        aspect_ratio = image_width/image_height

        display_height = 500
        display_width = display_height*aspect_ratio
        image_display = gr.Image(
            pil_image, 
            interactive=False, 
            width=display_width, 
            height=display_height
        )

        return image_display

    def get_app_obj(self):
        return self.app_obj

    def build(self):
        with gr.Blocks() as self.app_obj:
            # search_textbox = gr.Textbox(label='Query')
            search_button = gr.Button('Search')
            files_list = gr.Dataframe(
                headers=['Files names'],
                interactive=False,
                type='array'
            )

            image_display = gr.Image(interactive=False)

            files_list.select(
                self.selection_handler_func,
                files_list, 
                image_display
            )

            search_button.click(
                self.list_files_handler_func,
                files_list,
                files_list
            )

class Delete_Files_Interface(Base_Interface):

    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('config.cfg')

    def list_files_handler_func(self):
        files_list_output_df = self.handlers['list_files_handler_func']()

        return files_list_output_df

    def get_app_obj(self):
        return self.app_obj

    def build(self):
        with gr.Blocks() as self.app_obj:
            files_list = gr.CheckboxGroup(
                [],
                label="Files names", 
                info="Choose the files you want to delete"
            )
