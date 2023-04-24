import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from langchain import PromptTemplate, OpenAI, LLMChain
import yaml


class RouterConfig:
    def __init__(self, llm=None):
        self.chain_map = {}
        chroma_client = chromadb.Client()
        sentence_transformer_ef = SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
        self.router_coll = chroma_client.create_collection(name='router', embedding_function=sentence_transformer_ef)
        if not llm:
            llm = OpenAI(temperature=0.9)
        with open('model_specs.yml', 'r') as fp:
            content = yaml.safe_load(fp)
            for model in content.get('models'):
                for mname, mcontent in model.items():
                    mname = mname.lower()
                    self.router_coll.add(ids=[str(x) for x in range(len(mcontent.get('qa_maker')))],
                                         documents=mcontent.get('qa_maker'),
                                         metadatas=[{'classification': mname} for x in
                                                    range(len(mcontent.get('qa_maker')))])
                    self.chain_map[mname] = LLMChain(llm=llm, prompt=PromptTemplate(template=mcontent.get('template'),
                                                                                    input_variables=mcontent.get(
                                                                                        'input_vars')))

    def get_chains(self):
        return self.chain_map

    def get_embedding(self):
        return self.router_coll


if __name__ == '__main__':
    b = RouterConfig()
    c = b.get_chains()
