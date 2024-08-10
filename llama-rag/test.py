from langchain_community.document_loaders import PDFPlumberLoader
loader = PDFPlumberLoader("11pests1disease.pdf")
docs = loader.load()

# Check the number of pages
print("Number of pages in the PDF:",len(docs))

# Load the random page content
docs[2].page_content

print(docs[2].page_content)

## chunk the document

from langchain_experimental.text_splitter import SemanticChunker
from langchain_community.embeddings import HuggingFaceEmbeddings

text_splitter = SemanticChunker(HuggingFaceEmbeddings())
documents = text_splitter.split_documents(docs)

# Check number of chunks created
print("Number of chunks created: ", len(documents))
# Output 
"""
Number of chunks created:  23
"""

# Printing first few chunks
for i in range(len(documents)):
    print()
    print(f"CHUNK : {i+1}")
    print(documents[i].page_content)


## Create embeddings for each chunk 

from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# Instantiate the embedding model
embedder = HuggingFaceEmbeddings()

# Create the vector store with the documents from the pdf
vector = FAISS.from_documents(documents, embedder)


## Retrival from vector database

# Input
retriever = vector.as_retriever(search_type="similarity", search_kwargs={"k": 3})

# This gets the chunks of paragraphs relevent to the "invocation"
retrieved_docs = retriever.invoke("How does plant respond to disease?")

#print("RETRIEVED_DOCS:", retrieved_docs)


print("Documents retrived")

## Generation time

from langchain_community.llms import Ollama

# Define llm
llm = Ollama(model="llama3.1") # was mistral 
print(llm)


## GENERATION

from langchain.chains import RetrievalQA
from langchain.chains.llm import LLMChain
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.prompts import PromptTemplate

prompt = """
1. Use the following pieces of context to answer the question at the end.
2. If you don't know the answer, just say that "I don't know" but don't make up an answer on your own.\n
3. Keep the answer crisp and limited to 3,4 sentences.

Context: {context}

Question: {question}

Helpful Answer:"""


QA_CHAIN_PROMPT = PromptTemplate.from_template(prompt) 

llm_chain = LLMChain(
                  llm=llm, 
                  prompt=QA_CHAIN_PROMPT, 
                  callbacks=None, 
                  verbose=True)

document_prompt = PromptTemplate(
    input_variables=["page_content", "source"],
    template="Context:\ncontent:{page_content}\nsource:{source}",
)

combine_documents_chain = StuffDocumentsChain(
                  llm_chain=llm_chain,
                  document_variable_name="context",
                  document_prompt=document_prompt,
                  callbacks=None,
              )

qa = RetrievalQA(
                  combine_documents_chain=combine_documents_chain,
                  verbose=True,
                  retriever=retriever,
                  return_source_documents=True,
              )

# Input
print(qa("How does plant respond to disease?")["result"])
