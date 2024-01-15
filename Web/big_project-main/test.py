# import pandas as pd
# from langchain.vectorstores import Chroma
# from langchain.embeddings import OpenAIEmbeddings
# from langchain.embeddings import HuggingFaceEmbeddings
# from langchain.text_splitter import RecursiveCharacterTextSplitter
# from langchain.chat_models import ChatOpenAI
# from langchain.chains import RetrievalQA
# # from langchain.document_loaders import TextLoader
# # from langchain.document_loaders import DirectoryLoader
# from langchain.document_loaders.csv_loader import CSVLoader
# from collections import Counter

# df = pd.read_csv('company_data_files\cards.csv')

# loader = CSVLoader(file_path='company_data_files\cards.csv', source_column='cop', encoding='utf-8')
# data = loader.load()
# #print(data[0])

# text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
# texts = text_splitter.split_documents(data)

# #print('분할된 텍스트의 개수 :', len(texts))

# model_name = "jhgan/ko-sroberta-multitask"
# model_kwargs = {'device': 'gpu'}
# encode_kwargs = {'normalize_embeddings': False}

# hf = HuggingFaceEmbeddings(
#     model_name=model_name,
#     model_kwargs=model_kwargs,
#     encode_kwargs=encode_kwargs
# )

# vectordb_hf = Chroma(persist_directory="chroma_db_hf", embedding_function=hf)

# print(vectordb_hf)