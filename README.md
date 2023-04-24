## LangChain Conversational Model Router

Langchain provides several types of chaining where one model can be chained to another. A common design
pattern that'd be desired is for a hub-spoke model where one interface is presented to the end user/application
and the results need to come from multiple specialized models/chains/agents.

This implementation seeks to provide a design pattern for achieving the above goal.

### Features

- Supports a `chainMap` which can be a collection of chains that need to be serving behind single chain.
- Ability to freely customize each chain using its prompt templates and chain type preferences.
- Leverages embeddings using `chroma` to take Q&A samples for each model/LLM chain and be able to use it towards the
  routing decision.
- Conversational Memory with fail-safe mechanism to fall back to most recent history context if embedding match is not
  meeting threshold requirements for deciding the route. Great for abstract comments like `tell me more...`.
- Demonstrated using a chat application.

### Introducing ConversationalRouterChain

`ConversationalRouterChain` is the new custom chain that abstracts all the router implementation including memory
management, embedding query for match and threshold management.This chain type will be eventually merged into the
langchain ecosystem.
As of this time Langchain Hub submission is also under process to make it part of the official list of custom chains
that can be used by the open source community.

### Working with ConversationalRouterChain

- populate a `model_specs.yml` file with all the required destination chains to route. See sample for what's included.
- Set up the vector embedding as a `chroma` collection and pass it as a parameter to the chain.

See sample utility in `RouterConfig` class that sets up the chain map and the embedding.

```commandline
    chain_config = RouterConfig()
    # set up router chain
    router_chain = ConversationalRouterChain(llm=llm, chains=chain_config.get_chains(),
                                             vector_collection=chain_config.get_embedding(),
                                             memory=ConversationBufferWindowMemory(k=1), 
                                             verbose=True)
```

### Contributions and Feedback

There can be several ways this implementation can evolve to make it a really generic manifest definition based
chain/agent topology creation. Please provide feedback by either creating issues or forking this project and submitting
a PR. Some initial considerations:

- Support for more varieties of chains from destination. Provide capability to do n-level deep chain topologies.
- Extend support for hybrid Chain/Agent topology. Some Chains could be 'decision makers' while some agents could be executors and somewhere in between. 
- More robust observability and dynamic threshold management for memory. 

