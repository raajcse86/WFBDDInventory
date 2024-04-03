import chromadb
import streamlit as st
from streamlit_tags import st_tags
import pandas as pd
import json
import time
from pandas import DataFrame
# from sentence_transformers import SentenceTransformer
import plotly.figure_factory as ff



# model = SentenceTransformer('paraphrase-MiniLM-L3-v2')
# client = chromadb.EphemeralClient()
client = chromadb.Client()
# client = chromadb.PersistentClient(path="bddinventory_db")

import os


#streamlit application
st. set_page_config(layout='wide')

st.title('BDD Inventory Search Application')


# col1, col2 = st.columns(2)
keywords = st_tags(
    label='# Enter Keywords:',
    text='Press enter to add more',
    value=['Credit'],
    suggestions=['HMDA', 'Property', 'lightRiskEngine', 
                 'productPricingRatesUI', 'LRERequestDecision', 'declarationsUI', 
                 ],
    maxtags = 4,
    key='1')

# query_search = st.text_input("Enter Search Text", value="credit")

query_search=""

for keyword in keywords:
    query_search=query_search+keyword
    query_search=query_search+" "

resultCount = st.slider('Count Looking for ?', 0, 30, 10)

# with st.spinner('Operation In Progress...'):
#     time.sleep(5)

def read_files_from_folder(folder_path):
    file_data = []
    splittedLines = []

    for file_name in os.listdir(folder_path):
        if file_name.endswith(".txt"):
            with open(os.path.join(folder_path, file_name), 'r') as file:
                read = file.readlines()

    for line in read:
      line=line.strip()
      splittedLines = line.split(" ")
      file_data.append({"file_name":splittedLines[-1],"package_name":splittedLines[0]})
      splittedLines = []
    return file_data

folder_path = "bddinv"  # your folder path
file_data = read_files_from_folder(folder_path)

# for data in file_data:
#     print(f"File Name: {data['file_name']}")
#     print(f"Package Name: {data['package_name']}\n")

documents = []
embeddings = []
metadatas = []
ids = []
# def enumerateFileData(model, file_data, documents, embeddings, metadatas, ids):
#     for index,data in enumerate(file_data):
#       documents.append(data['file_name'])
#       embeding = model.encode(data['package_name']+" "+data['file_name']).tolist()
#       embeddings.append(embeding)
#       metadatas.append({'package':data['package_name']})
#       ids.append(str(index+1))

# enumerateFileData(model, file_data, documents, embeddings, metadatas, ids)

def enumerateFileData(file_data, documents,metadatas, ids):
    for index,data in enumerate(file_data):
      documents.append(data['package_name']+" "+data['file_name'])
      metadatas.append({'package':data['package_name'],'file_name':data['file_name']})
      ids.append(str(index+1))
enumerateFileData(file_data, documents,metadatas, ids)

# documents

# def createOrGetCollection(client, documents, embeddings, metadatas, ids):
#     bdd_inv_collection = client.get_or_create_collection("bdd_inv_collection")
#     if bdd_inv_collection.count() <= 0:
#         bdd_inv_collection.add(
#         documents=documents,
#         embeddings=embeddings,
#         metadatas=metadatas,
#         ids=ids
#     )
        
#     return bdd_inv_collection

# bdd_inv_collection = createOrGetCollection(client, documents, embeddings, metadatas, ids)

def createOrGetCollection(client, documents,metadatas, ids):
    bdd_inv_collection = client.get_or_create_collection("bdd_inv_collection")
    if bdd_inv_collection.count() <= 0:
        bdd_inv_collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )
        
    return bdd_inv_collection

bdd_inv_collection = createOrGetCollection(client, documents,metadatas, ids)


def queryByEmbeddingSearch(resultCount, bdd_inv_collection, input_em):
    results = bdd_inv_collection.query(
    query_embeddings=[input_em],
    n_results=resultCount
)
def queryByNonEmbeddingSearch(resultCount, bdd_inv_collection, query_search):
    results = bdd_inv_collection.query(
    query_texts=[query_search],
    n_results=resultCount,
    # where={
    #         "package":
    #             { 
    #                 "$eq": query_search
    #             }
    #         },
    # where_document={"$contains":query_search}
)    
    return results

finalResultsIds=[]
finalResultsDistances=[]
finalResultsMetadatas=[]
finalResultsFileNames=[]
finalResults=[]
finalPlotResults=[]
finalPlotFileNames=[]
def enumerateQueryResult(results, finalResultsIds, finalResultsDistances, finalResultsMetadatas, finalResultsFileNames):
    for res in results:
        if ((results[res] != None) and (res == 'ids')):
            for re in results[res]:
                for r in re:
                    finalResultsIds.append(r) 
        elif ((results[res] != None) and (res == 'distances')):
            for re in results[res]:
                for r in re:
                    finalResultsDistances.append(r)
        elif ((results[res] != None) and (res == 'metadatas')):
            for re in results[res]:
                for r in re:
                    finalResultsMetadatas.append(r)
        elif ((results[res] != None) and (res == 'documents')):
            for re in results[res]:
                for r in re:
                    finalResultsFileNames.append(r)

if ((query_search != None) and (len(query_search) > 0)):
    # input_em = model.encode(query_search).tolist()
    # results = queryByEmbeddingSearch(resultCount, bdd_inv_collection, input_em)

    results = queryByNonEmbeddingSearch(resultCount, bdd_inv_collection, query_search)

    enumerateQueryResult(results, finalResultsIds, finalResultsDistances, finalResultsMetadatas, finalResultsFileNames)
    # print(f"Documents >>  {finalResultsFileNames}")
    # print(f"IDS >> {finalResultsIds}")
    # print(f"Distances >> {finalResultsDistances}")
    # print(f"MetaDatas >> {finalResultsMetadatas}")
    for index in range(len(finalResultsIds)):
            finalResults.append({"Ids":finalResultsIds[index],
                                "Distances":finalResultsDistances[index],
                                "FileName":finalResultsFileNames[index],
                                "MetaDatas":finalResultsMetadatas[index]}
                                )
            finalPlotResults.append({"Distances":finalResultsDistances[index],
                                     "FileName":finalResultsFileNames[index]
                                     })
            finalPlotFileNames.append({"FileName":finalResultsFileNames[index]})
    if len(finalResults) >0:
        st.success('This is a success message!', icon="✅")
        # st.balloons()
        df = pd.DataFrame(finalResults)
        st.dataframe(df)

        st.markdown("SCATTER CHART")
        dfplot = pd.DataFrame(finalPlotResults,columns=["Distances"])

        st.scatter_chart(dfplot)

        st.markdown("BAR CHART")
        st.bar_chart(dfplot)

        st.markdown("LINE CHART")
        st.line_chart(dfplot)



    else:
        st.info('No file matching the keywords', icon="ℹ️")
else:
    st.error("Please Enter/Select some Keywords....")



