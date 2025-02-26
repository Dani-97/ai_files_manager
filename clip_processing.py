import configparser
from gradio_client import Client, handle_file
import numpy as np
import os
import pandas as pd

class CLIP_Processing_Manager():

    def __init__(self):
        pass

    def get_index_metadata(self, csv_file_path):
        index_metadata = pd.DataFrame([])

        if ((csv_file_path!=None) and (os.path.exists(csv_file_path))):
            index_metadata = pd.read_csv(csv_file_path, index_col=False)

        return index_metadata

    def append_new_index_metadata(self, input_df, filepaths_list):
        images_embeddings = self.get_images_embeddings(filepaths_list)
        images_embeddings_df = pd.DataFrame(images_embeddings)
        headers_list = ['image_name'] + [f'feature_{it}' for it in range(0, images_embeddings.shape[1]-1)]
        images_embeddings_df.columns = headers_list
        input_df = pd.concat([input_df, images_embeddings_df], ignore_index=True)

        return input_df

    def store_index_metadata(self, input_df, csv_file_path):
        input_df.to_csv(csv_file_path, index=False)

    def get_images_embeddings(self, images_paths_list):
        config = configparser.ConfigParser()
        config.read('config.cfg')
        client = Client(config['GRADIO_CLIENTS']['ENDPOINT_IMAGE_EMBEDDINGS'])
        
        images_embeddings_list = []
        input_image_paths_list = list(map(lambda input_value: handle_file(input_value), images_paths_list))

        images_embeddings = client.predict(
                input_image_paths_list=input_image_paths_list,
                api_name="/predict"
        )
        images_embeddings = np.array(images_embeddings['value']['data'])

        return images_embeddings

    def search_images_by_text(self, text_prompt, images_embeddings_df):
        config = configparser.ConfigParser()
        config.read('config.cfg')
        client = Client(config['GRADIO_CLIENTS']['ENDPOINT_TEXT_EMBEDDINGS'])

        images_embeddings = images_embeddings_df.values.tolist()
        headers_list = ['image_name'] + [f'feature_{it}' for it in range(0, images_embeddings_df.shape[1]-1)]
        search_results = client.predict(
                text_prompt = text_prompt,
                input_np_array = {
                    "headers": headers_list, 
                    "data": images_embeddings
                },
                api_name="/predict"
        )
        
        # We discard search_results[0] given that it returns the embeddings of the text prompt and,
        # in this case, that is not necessary.
        headers_list = search_results[1]['headers']
        search_results = pd.DataFrame(search_results[1]['data'])
        search_results.columns = headers_list

        images_names_list = search_results['image_name'].values.tolist()
        images_names_list = list(map(lambda input_value: os.path.basename(input_value), images_names_list))

        return images_names_list