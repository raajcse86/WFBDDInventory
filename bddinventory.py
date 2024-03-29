import chromadb
import streamlit as st 
import pandas as pd
import json

from pandas import DataFrame
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('paraphrase-MiniLM-L3-v2')
client = chromadb.EphemeralClient()
client = chromadb.PersistentClient(path="bddinventory_db")

import os


#streamlit application
st. set_page_config(layout='wide')

st.title('BDD Inventory Search Application')


col1, col2 = st.columns(2)
query_search = col1.text_input("Enter Search Text", value="credit")
resultCount = col1.number_input("Count Looking for", min_value=0, value=10)


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

for data in file_data:
    print(f"File Name: {data['file_name']}")
    print(f"Package Name: {data['package_name']}\n")

documents = []
embeddings = []
metadatas = []
ids = []
for index,data in enumerate(file_data):
  documents.append(data['file_name'])
  embeding = model.encode(data['package_name']+" "+data['file_name']).tolist()
  embeddings.append(embeding)
  metadatas.append({'package':data['package_name']})
  ids.append(str(index+1))

# documents

bdd_inv_collection = client.get_or_create_collection("bdd_inv_collection")
if bdd_inv_collection.count() <= 0:
    bdd_inv_collection.add(
        documents=documents,
        embeddings=embeddings,
        metadatas=metadatas,
        ids=ids
    )




# query = "liability"
input_em = model.encode(query_search).tolist()

results = bdd_inv_collection.query(
    query_embeddings=[input_em],
    n_results=resultCount
)

finalResultsIds=[]
finalResultsDistances=[]
finalResultsMetadatas=[]
finalResultsFileNames=[]
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


# print(f"Documents >>  {finalResultsFileNames}")
# print(f"IDS >> {finalResultsIds}")
# print(f"Distances >> {finalResultsDistances}")
# print(f"MetaDatas >> {finalResultsMetadatas}")

finalResults=[]
for index in range(len(finalResultsIds)):
    finalResults.append({"Ids":finalResultsIds[index],
                        "Distances":finalResultsDistances[index],
                        "FileName":finalResultsFileNames[index],
                        "MetaDatas":finalResultsMetadatas[index]}
                        )

df = pd.DataFrame(finalResults)
st.success("Search Results")
st.dataframe(df)





