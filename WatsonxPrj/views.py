from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.shortcuts import render



from .apis import uploader
from .apis import embedder
from .apis import query



@api_view(['GET'])
def hello_world(request):
    #print(request.method)
    return Response("hello")




@api_view(['post'])
def process_all_cvs(request):
    """
    Process all CV docs files, create CSV files and upload to watsonx.data to create cv_data table.
    POST http://127.0.0.1:8000/process_all_cvs/
    Sample Body Request Payload :
      {
            "cv_docx_files": ["WatsonxPrj/data/cv1.docx", "WatsonxPrj/data/cv2.docx", "WatsonxPrj/data/cv3.docx", "WatsonxPrj/data/cv4.docx", "WatsonxPrj/data/cv5.docx"],
            "cv_csv_folder" : "WatsonxPrj/data",
            "cv_wxd_table" : "profile_cv",
            "cv_wxd_target_table" : 'profile_target_cv"
        }
    """
    resp= uploader.process_cv_files(request)
    return Response(resp)   


@api_view(['post'])
def embeddings(request):
    """
    Embedding vector data of  CV csv file into the MongoDB.
    POST http://127.0.0.1:8000/embeddings/
    Sample Body Request Payload :
        {
           "cv_wxd_table": "profile_cv"
        }
    """   
    resp =embedder.embeddings(request)
    return Response(resp)

@api_view(['post'])
def cv_screening(request): 
    """
    CV screening by asking query.
    POST http://127.0.0.1:8000/cv_screening/
    Sample Body Request Payload :
        {
            "cv_screening_query": "Give me name and skills of senior Web Developer specializing in front end development"
        }
    """   
    resp = query.get_response(request)
    return Response(resp)
