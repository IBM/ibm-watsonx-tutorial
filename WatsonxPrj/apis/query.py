import sys
import os
sys.path.append('<workspace>\\Django-Prj\\WatsonxPrj\\WatsonxPrj')
''' ----------------------------------------------------'''
import requests
    
from WatsonxPrj.apis.embedder import huggingface_embeddins
from WatsonxPrj.apis.prompt import WATSONX_PROMPT
from pymongo import MongoClient

from dotenv import load_dotenv
load_dotenv(dotenv_path="../.env")


def get_prompt_embeddings(prompt_q:str)->list:
    return huggingface_embeddins(prompt_q)
    
def retrive_embedddings_map_list(embeddings, top_count:int):
    embedddings_map_list=[]
    connection_url=  os.environ.get("MONGODB_CONN_URL") 
    collection_name='gai_embeddings'
    clnt = MongoClient(connection_url, ssl=True,ssl_cert_reqs='CERT_NONE')
    database_name="mytest_DB"
    db_obj = clnt.get_database(database_name) 
    collec=db_obj[collection_name]
    embedding_field_name="embeddings" #name of the search vector field
    no_nn=4 #Number of nearest neighbors (k-nn) to return
    limit=top_count  #number of results limit to
    srch_ndx="mytestDB_embedding_ndx1" #search index of type knnVector to create for this collection for field 'embeddings'
    
    """
    Make sure srch_ndx should have 'embeddings' field indexed of type knnVector as below '
    {
      "mappings": {
        "dynamic": true,
        "fields": {
          "embeddings": {
            "dimensions": 384,
            "similarity": "dotProduct",
            "type": "knnVector"
          }
        }
      }
    }
    """
    results= collec.aggregate([
            {
                '$search': {
                    "index": srch_ndx,
                    "knnBeta": {
                        "vector": embeddings,
                        "k": no_nn, 
                        "path": embedding_field_name
                        }
                }
            },
            {
            "$limit": limit  #number of results limit to
            },
            {
            "$project": {
              "_id": 0,
              "paragraph": 1, # The name of the field which holds the text of corresponding vector embedding 
              "score": { '$meta': "searchScore" }
            }
        
          }
        ])
    for document in results:
        embedddings_map_list.append(document)
    return  embedddings_map_list                                     
    

def get_bearer_token(apikey):

    body = {'apikey': apikey, 'grant_type': "urn:ibm:params:oauth:grant-type:apikey"}
    response = requests.post("https://iam.cloud.ibm.com/oidc/token", data = body)
    if response.status_code != 200:
        raise Exception("Failed to get bearer token, invalid status")
    json = response.json()
    if not json:
        raise Exception("Failed to get bearer token, invalid response")
    return json.get("access_token")

def generate_watsonx_ai_text(text, question):
    
    text=text.replace('\n',' ')
    
    gen_text=''
    
    prompt_context_template="<<CONTEXT>>"
    prompt_question_template="<<QUESTION>>"

     
  
    # 1. Load environment variables
    url = os.environ.get("WATSONX_URL")
    print(f"***LOG: - url: {url}")
    api_key=os.environ.get("IBMCLOUD_APIKEY")

    # 2. Get access token
    token= get_bearer_token(api_key)
    
    bearer_auth = f"Bearer {token}" 
    model_id = os.environ.get("WATSONX_LLM_NAME")
    min_tokens =os.environ.get("WATSONX_MIN_NEW_TOKENS")
    max_tokens = os.environ.get("WATSONX_MAX_NEW_TOKENS")
    prompt = os.environ.get("WATSONX_PROMPT")   #WATSONX_PROMPT  #
    project_id = os.environ.get("WATSONX_PROJECT_ID")
    version = os.environ.get("WATSONX_VERSION")    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": bearer_auth
    }
    params = {
         "version": version
    }
    
    # 5. Build the prompt with context documents and question
    input_txt = prompt.replace(prompt_context_template,text)
    print("Document Text:-->\n------------------\n", input_txt)
    
    data_input = input_txt.replace(prompt_question_template,question)
    
    print("Questions:-->\n------------------\n", data_input)

    
    # 6. Create payload
    json_data = {
            "model_id": model_id,
            "input": data_input,
            "parameters":{
                "decoding_method": "greedy",
                "min_new_tokens": int(min_tokens),
                "max_new_tokens": int(max_tokens),
                "beam_width": 1
            },
             "project_id": project_id      
    }
    
    # 6. Invoke REST API
    response = requests.post(
        url,
        headers=headers,
        params=params,
        json=json_data
    )
    #print(f"Response: {response}")
         
    # 7. Verify result and extract answer from the return vaule
    if (response.status_code == 200):
            data_all=response.json()
            results = data_all["results"]
            gen_text = results[0]["generated_text"]
    
    return gen_text

def  marged_paragraphs(embeddings_map_list): 
    paras=[] 
    for item in embeddings_map_list:
        paras.append(item['paragraph'])
    return " ".join(paras)

def get_response(request):
    
    query_prompt = request.data.get('cv_screening_query') if request else \
                                    "Give me name and skills of senior Web Developer specializing in front end development"
    print("Query-->", query_prompt)
    embeddings= get_prompt_embeddings(query_prompt)
    print("Got questions embeddings-->")
    embeddings_map_list= retrive_embedddings_map_list(embeddings, top_count=2)
    print("Got top 2 search embeddings-->")
    text= marged_paragraphs(embeddings_map_list)
    print("Got the input text")
    gen_txt=generate_watsonx_ai_text(text, query_prompt)
    print("Generated text:", gen_txt)
    return gen_txt

if __name__=="__main__":     
    get_response(None)
        
