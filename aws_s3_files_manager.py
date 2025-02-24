import boto3
import configparser
import pandas as pd

class Files_Manager():

    def __init__(self):
        self.config = configparser.ConfigParser()
        self.config.read('config.cfg')

    def configure_credentials(self):
        ACCESS_KEY = self.config['USER']['ACCESS_KEY']
        SECRET_KEY = self.config['USER']['SECRET_KEY']

        self.session = boto3.Session(
            aws_access_key_id=ACCESS_KEY,
            aws_secret_access_key=SECRET_KEY,
        )

        self.client = boto3.client(
            's3',
            aws_access_key_id=ACCESS_KEY,
            aws_secret_access_key=SECRET_KEY
        )

    def initialize_dataframe(self):
        init_df = pd.DataFrame([])
        init_df.columns = ['Files names']

        return init_df

    def upload_file(self, file_path, object_name):
        BUCKET_ID = self.config['BUCKET']['BUCKET_ID']
        
        self.client.upload_file(file_path, BUCKET_ID, object_name)

    def list_objects(self):
        BUCKET_ID = self.config['BUCKET']['BUCKET_ID']

        s3_obj = self.session.resource('s3')
        bucket = s3_obj.Bucket(BUCKET_ID)

        files_names_list = []
        for item in bucket.objects.all():
            files_names_list.append(item.key)
    
        files_names_df = pd.DataFrame([])
        files_names_df['Files names'] = files_names_list
        
        return files_names_df

    def get_object(self, object_name):
        BUCKET_ID = self.config['BUCKET']['BUCKET_ID']
        
        response = self.client.get_object(
            Bucket=BUCKET_ID,
            Key=object_name,
        )

        return response

    def delete_object(self, object_name):
        BUCKET_ID = self.config['BUCKET']['BUCKET_ID']

        self.client.delete_object(Bucket=BUCKET_ID, Key=object_name)

    def download_object(self, object_name, local_dst_path):
        BUCKET_ID = self.config['BUCKET']['BUCKET_ID']

        self.client.download_file(BUCKET_ID, object_name, local_dst_path)

def main():
    file_manager_obj = Files_Manager()
    file_manager_obj.configure_credentials()

    list_objects_result = file_manager_obj.list_objects()

main()
