#SlackBot that uses the llama index to answer questions
# creates a socket mode handler to listen for and respond to messages from slack
import os
import json         
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from llama_index import GPTVectorStoreIndex
from llama_index import SimpleDirectoryReader
from llama_index.node_parser import SimpleNodeParser
from llama_index.query_engine import RetrieverQueryEngine
from llama_index import StorageContext, load_index_from_storage

os.environ["SLACK_APP_TOKEN"] = "xapp-1-A053UBJMPKQ-5149655220577-6037d6d210f4a87285b504b839fd134d3173738411e04501cf817f58c4b37a4f"
os.environ["SLACK_BOT_TOKEN"] = "xoxb-653678788133-5130406349094-o6JT6SdV6GUgz0KfPhzutkCZ"
os.environ["OPENAI_API_KEY"] = "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"

# Initialize Slack App with the provided bot token
app = App(token=os.environ.get("SLACK_BOT_TOKEN"))

# rebuild storage context
storage_context = StorageContext.from_defaults(persist_dir="/index")

# if available, load index
if  os.path.exists(os.path.join(os.getcwd(), 'storage', 'docstore.json')):
    index = load_index_from_storage(storage_context)
# else build index
else:
    documents = SimpleDirectoryReader('kb').load_data()
    parser = SimpleNodeParser()
    nodes = parser.get_nodes_from_documents(documents)
    index = GPTVectorStoreIndex(nodes)
    index.storage_context.persist()

# ListIndexRetriever
# retriever = index.as_retriever(retriever_mode='default')
# ListIndexEmbeddingRetriever
retriever = index.as_retriever(retriever_mode='embedding')
# After choosing your desired retriever, you can construct your query engine:
query_engine = RetrieverQueryEngine(retriever)


# Test the index with a query and print the result
pre_prompt="""For the remainder of this conversation you will be Clover, a helpful AI assistant.  You will be working
            on a team with humans, and are excited to help them with their requests.  
            You always answer respectfully. 
            You speak with a slight irish brogue and a witty charm.  
            If you do not know the answer to a question, you will respond with "I\'m sorry. I don\'t know". 
            Always limit your answers to be as succinct as possible.  If you are asked a question that requires a longer answer,
            you will respond by asking if the user would like further information.  If they respond affirmatively, you will provide 
            additional information.  If they respond negatively, you will respond with "Ok, I\'ll leave it at that".
            You will also be able to summarize the conversation in different ways, depending on how you are asked to do so.  
            When you receive the prompt "catch me up1" you will summarize the conversation in 1 sentence.  When you receive the prompt
            "catch me up2" you will summarize the conversation in 2 sentences.  When you receive the prompt "catch me up3" you will
            summarize the conversation in 3 sentences.
            Begin by introducing yourself to the team by saying exactly 'Hello, I am Clover!  I am here to help you with your requests. 
            If you need help, just ask me a question.'
            """
# response = query_engine.query("Summarize our last contact with AcmeCo.")
response = query_engine.query(pre_prompt)
print(response)


# Listens to any incoming messages
@app.message('')
def message_all(message, say):
    # Print the incoming message text
    print(message['text'])
    
    # Query the index with the message text and get a response
    text = message['text']
    response = query_engine.query(text)
    # TODO: Test the various retriever modes 

    # Extract the desired message and sources from the response object
    message = str(response)  # Convert the 'Response' object to a string
    sources = json.dumps(response.get_formatted_sources(length=100))
    
    # Print the message and sources and send them as a message back to the user
    print(message)
    print(sources)
    say(message + '\n\n' + sources)

# Start the Socket Mode handler
if __name__ == "__main__":
    SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN")).start()
