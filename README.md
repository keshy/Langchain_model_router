## LangChain Conversational Model Router

With several types of model orchestration and topologies becoming a need, we have a fairly common design pattern of orchestrating multiple LLM models via a single conversational chat/completion interface.
This implementation seeks to address that need. 

### Concepts

The implementation follows the pattern suggested by LangChain implementations where the base implementation is `LLMChain`. Given the custom need, a new LLM chain is proposed. 
The key requirements here include

- Lightweight and configurable system that can scale to 100s of LLM models being behind a single conversational interface 
- Ability of the conversational interface to route efficiently to corresponding models. 
- Ability for the interface to maintain required history that's relevant for the scope of the conversational experience. 

### Features

- The implementation uses a manifest driven LLM chain generation. See `model_specs.yml` for more details. 
- The same manifest includes some prompt samples to help train with an embedding. 
- Uses chroma vector embeddings to be able to analyze a question and route it to the right model. 
- Scope of error is minimal and guardrails have been added to prevent `hallucintion swaps` as it tries to answer chain-of-thought questions that can span multiple models. 

### Usage
```
$> pip install -r requirements.txt
$> python3 main.py
```
Ensure that the following environment variables are set:
- OPENAI_API_KEY with the key from OpenAI or Azure OpenAI 
- PyTorch parallelism disabled. You'll see an initial error with the same suggestion to prevent false positive issues. 



