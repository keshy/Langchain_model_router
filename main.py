from chromadb.api.models.Collection import Collection
from langchain.chains import LLMChain
from langchain.chains.base import Chain

from typing import Dict, List, Any
from langchain.indexes import VectorstoreIndexCreator
import pandas as pd
import os

from datetime import datetime
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.input import get_color_mapping
from langchain.llms import OpenAI
from langchain.memory import VectorStoreRetrieverMemory
from langchain.chains import LLMChain
import chromadb
from chromadb.utils.embedding_functions import SentenceTransformerEmbeddingFunction
from langchain.prompts import PromptTemplate
import os

from pydantic import Extra, root_validator


class SimpleRouterChain(Chain):
    """Simple chain where the outputs of one step feed directly into next."""

    chains: Dict[str, Chain]
    strip_outputs: bool = False
    input_key: str = "input"  #: :meta private:
    output_key: str = "output"  #: :meta private:
    vector_collection: Collection = None

    class Config:
        """Configuration for this pydantic object."""
        extra = Extra.forbid
        arbitrary_types_allowed = True

    @property
    def input_keys(self) -> List[str]:
        """Expect input key.

        :meta private:
        """
        return [self.input_key]

    @property
    def output_keys(self) -> List[str]:
        """Return output key.

        :meta private:
        """
        return [self.output_key]

    def _call(self, inputs: Dict[str, str]) -> Dict[str, str]:
        _input = inputs[self.input_key]
        color_mapping = get_color_mapping([str(x) for x in self.chains.keys()])
        if not self.vector_collection:
            raise ValueError("Router embeddings in SimpleRouterPipeline is empty or not provided.")
        x = self.vector_collection.query(query_texts=[_input], n_results=3)
        classification, distance = x['metadatas'][0][0], x['distances'][0][0]
        _input = self.chains[classification['classification']](_input)
        if self.strip_outputs:
            _input = _input.strip()
        self.callback_manager.on_text(
            _input, color=color_mapping[classification['classification']], end="\n", verbose=self.verbose
        )
        return {self.output_key: _input}


if __name__ == "__main__":
    asset_search_prompt = PromptTemplate(
        input_variables=["sentence"],
        template="""
              Assume the role of a forensic investigator and answer the question below based on what data you already know 
              
              Forensic Question on Asset Search:               
              {sentence}
        """
    )
    router_df = pd.read_csv('pc_router.csv')
    chroma_client = chromadb.Client()
    sentence_transformer_ef = SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
    router_coll = chroma_client.create_collection(name='router', embedding_function=sentence_transformer_ef)

    for index, row in router_df.iterrows():
        router_coll.add(ids=[str(index)], documents=[row['text']],
                        metadatas=[{'classification': row['label']}])
    llm = OpenAI(temperature=0.9, openai_api_key='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')
    forensic_specialist = LLMChain(llm=llm, prompt=asset_search_prompt)
    # tea_speacialist = LLMChain(llm=llm, prompt=BaseModelConfigs(template="""
    #     Assume the role of a tea specialist who can brew good tea and teach others. Answer the question below in the most succinct way possible
    #
    #     {sentence}
    #
    # """, human_input_variable=['sentence']))

    chain_map = {
        # 'explainer': self.explainer_chain,
        # 'config_search': self.config_search_chain,
        'asset_search': forensic_specialist,
        # 'tea_search': tea_speacialist
        # 'network_search': self.network_search_chain,
        # 'audit_search': self.audit_search_chain,
        # 'iam_search': self.iam_search_chain,
        # 'cna_search': self.cna_search_chain,
        # 'command_center': self.command_center_chain,
        # 'how_to': self.how_to_chain,
        # 'onboarding': self.onboarding_chain
    }
    router_chain = SimpleRouterChain(chains=chain_map, vector_collection=router_coll)
    concat_output = router_chain.run("Search for an asset that is exposed to the internet and has serious problems")
    print(f"output:\n{concat_output}")
