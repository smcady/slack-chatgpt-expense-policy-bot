import os
os.environ["SLACK_APP_TOKEN"] = "xapp-1-A053UBJMPKQ-5149655220577-6037d6d210f4a87285b504b839fd134d3173738411e04501cf817f58c4b37a4f"
os.environ["SLACK_BOT_TOKEN"] = "xoxb-653678788133-5130406349094-o6JT6SdV6GUgz0KfPhzutkCZ"
os.environ["OPENAI_API_KEY"] = "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"
from llama_index import SimpleDirectoryReader
from llama_index.node_parser import SimpleNodeParser
from llama_index import GPTVectorStoreIndex
from llama_index.query_engine import RetrieverQueryEngine
from llama_index import StorageContext, load_index_from_storage

# rebuild storage context
storage_context = StorageContext.from_defaults(persist_dir="/index")

# if # load index
# 
if  os.path.exists(os.path.join(os.getcwd(), 'storage', 'docstore.json')):
    index = load_index_from_storage(storage_context)
# else build index
else:
    documents = SimpleDirectoryReader('kb').load_data()
    parser = SimpleNodeParser()
    nodes = parser.get_nodes_from_documents(documents)
    index = GPTVectorStoreIndex(nodes)
    index.storage_context.persist()

# TODO: Test the various retriever modes 
# ListIndexRetriever
# retriever = index.as_retriever(retriever_mode='default')
# ListIndexEmbeddingRetriever
retriever = index.as_retriever(retriever_mode='embedding')
# After choosing your desired retriever, you can construct your query engine:

query_engine = RetrieverQueryEngine(retriever)
response = query_engine.query("Summarize our last contact with AcmeCo.")


print(response)


