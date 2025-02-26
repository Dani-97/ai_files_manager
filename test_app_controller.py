from app_controller import AppController
import os

def main():
    input_root_dir = './test_imgs'
    app_controller_obj = AppController()

    objects_names_list = os.listdir(input_root_dir)
    files_paths_list = list(map(lambda input_value: f'{input_root_dir}/{input_value}', objects_names_list))
    app_controller_obj.upload_files_handler_func(files_paths_list, objects_names_list)
    images_names_list = app_controller_obj.search_files_by_text_prompt_handler_func('bear')

    print(images_names_list)

main()