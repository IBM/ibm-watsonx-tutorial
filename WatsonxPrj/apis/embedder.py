
import requests
import re
import os
from pymongo import MongoClient
from ibm_watsonxdata import WatsonxDataV1
from WatsonxPrj import settings

from dotenv import load_dotenv
load_dotenv(dotenv_path="../.env")


def huggingface_embeddins(para:str)->list:
    BASE_URL = os.environ.get("HF_BASE_URL")
    EMBEDDING_MODEL = os.environ.get("HF_EMBEDDING_MODEL")  
    hf_token = os.environ.get("HF_TOKEN") #hugingface token
    embedding_url=f"{BASE_URL}/pipeline/feature-extraction/sentence-transformers/{EMBEDDING_MODEL}"
    response = requests.post(
            embedding_url,
            headers={"Authorization": f"Bearer {hf_token}"},
            json={"inputs": para})
    if response.status_code != 200:
        print("ERROR: huggingface embedding response code:",response.status_code  )
        print("ERROR: huggingface embedding response :",response.text  )
        raise ValueError(f"Request failed with status code {response.status_code}: {response.text}")
    
    return response.json()


def get_paragraphs(content:str):
    """
    Split large sentences into sections with given min no of words
    """
    min_words=200
    # Split the content into sentences
    sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?)\s', content)
    sections = []
    current_section = ""
    for sentence in sentences:
        words = sentence.split()
        if len(current_section.split()) + len(words) <= min_words:
            current_section += sentence + " "
        else:
            if current_section:
                sections.append(current_section.strip())
            current_section = sentence + " "
    if current_section:
        sections.append(current_section.strip())
    return sections
    
  

def get_paras(csv_file)->list:
    cv_paras_map_list=[]
    import pandas as pd
    df = pd.read_csv(csv_file,encoding='unicode_escape')
    #Iterate Pandas Dataframe
    for pd_tuple in df.itertuples(): 
        #print(pd_tuple)
        paras = get_paragraphs(pd_tuple.text_content)
        cv_paras_map={
            "file-name" :pd_tuple.file_name,
            "paras" :paras
            }
        cv_paras_map_list.append(cv_paras_map)
    return cv_paras_map_list 
        
def generate_embeddings(cv_paras_map_list:list)->list:
    para_embeddings_map_list=[]
    for cv_paras_map in  cv_paras_map_list:
        file_name=cv_paras_map["file-name"]
        paras= cv_paras_map["paras"]
        for para in paras:
            embeddings = huggingface_embeddins(para)
            para_embeddings_map_list.append(
                            {
                                "paragraph" :  f"{file_name} - {para}",
                                "embeddings" :  embeddings
                            }
                        ) 
    return para_embeddings_map_list


def upsert_embeddings(para_embeddings_map_list:list):
    result=None
    connection_url=   os.environ.get("MONGODB_CONN_URL")
    collection_name='gai_embeddings'
    clnt = MongoClient(connection_url, ssl=True,ssl_cert_reqs='CERT_NONE')
    database_name=  os.environ.get("MONGODB_DB_NAME")
    db_obj = clnt.get_database(database_name) 
    collec=db_obj[collection_name]
    try:
        for input_json in para_embeddings_map_list:
            if '_id' in input_json: 
                input_json.pop("_id")
            #insert unique record 
            result = collec.update_one(input_json, {'$set':input_json}, upsert=True)
            #result = collec.insert_one(input_json)
    except  Exception as err:
            raise err
    finally :
            # purpose over, close connection
            clnt.close()
            del clnt    
    return result


def download_csv_from_watsonx_data(cv_wxd_table):
    try:
        watsonx_data_host=os.environ.get("WATSONX_DATA_HOST")
        watsonx_data_inst_id=os.environ.get("WATSONX_DATA_INST_ID")
        watsonx_data_access_token=os.environ.get("WATSONX_DATA_ACCESS_TOKEN")
        headers = {
            'accept': 'application/json',
            # 'Content-Type': 'multipart/form-data',
            'AuthInstanceId': f'{watsonx_data_inst_id}',
            'LhInstanceId': f'{watsonx_data_inst_id}',
            'Authorization': f'Bearer {watsonx_data_access_token}',
            }
        params = {
            'engine_id': 'presto-01'
        }
        data = {
            'catalog': 'iceberg_data',
            'schema': "wx_profiles",
            'sqlQuery': f'SELECT * FROM "iceberg_data"."wx_profiles".{cv_wxd_table} LIMIT 10'
        }
        response = requests.post(
            f'{watsonx_data_host}/lakehouse/api/v1/{watsonx_data_inst_id}/v1/statement',
            params=params,
            headers=headers,
            data=data
        )
        if response.status_code==200:
            print(response._content)
            '''
            TODO: convert SQL run result content to csv_file under WatsonxPrj/data folder
            Disclaimer here
            '''
            return '' #'converted csv file'
        else:
            print("ERROR:  Downloading content from watsonx.data.  REASON-->", response._content )
            print("We used default cv_data.csv from local which was created during process-cv API, ")
    except Exception as ex:
        print("Error occurred:", str(ex))
        pass
    
    ''' Return default csv file '''
    csv_file=f"{settings.BASE_DIR}/WatsonxPrj/data/cv_data.csv"
    return csv_file
        
def embeddings(request):    
    cv_wxd_table = request.data.get('cv_wxd_table')     
    csv_file_path = download_csv_from_watsonx_data(cv_wxd_table)
    cv_paras_map_list=get_paras(csv_file_path)
    #print(cv_paras_map_list)
    print("got paragraph cv map list")
    para_embeddings_map_list=generate_embeddings(cv_paras_map_list)
    #print(para_embeddings_map_list)
    print("paragraph embedding map list, generated")
    rslt= upsert_embeddings(para_embeddings_map_list)
    print("embedding CV map list stored in MongoDB")
    return "Embeddings generated successfully for CSV file in MongoDB" if rslt else "Generation of embidding problem!. Try later."

if __name__=="__main__": 
    from dotenv import load_dotenv
    load_dotenv(dotenv_path="../.env")
    embeddings(None)
