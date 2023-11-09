# Langchain Token Usage

This repository contains a python module to track the consumption of tokens of a Large Language Models (LLMs) within a [LangChain](https://github.com/langchain-ai/langchain) application.

## Installation

You can install _LangChain Token Usage_ via [pip]:

```console
$ pip install git+https://github.com/mrtj/langchain_token_usage.git
```

or in requirements.txt:

```txt
langchain-token-usage @ git+https://github.com/mrtj/langchain_token_usage.git
```

## Usage

Token usage tracking is implemented as a [LangChain Callback](https://python.langchain.com/docs/modules/callbacks/) so it is easy to integrate in any LangChain application. The collection of the token usage metrics is LLM specific: currently only OpenAI LLMs are supported.

The metrics collected can be processed locally, or sent to a metrics repository via a Reporter. Current implementation includes sending the metrics to [Amazon CloudWatch](https://aws.amazon.com/cloudwatch/) service.

If you wish to use CloudWatch, you should ensure that you have [configured your boto3 client](https://boto3.amazonaws.com/v1/documentation/api/latest/guide/configuration.html) to credentials that are associated to an IAM Role that can write data to CloudWatch Metrics.

Example usage:

```python
from langchain.chains import LLMChain
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate

from langchain_token_usage.handlers import OpenAITokenUsageCallbackHandler
from langchain_token_usage.reporters import CloudWatchTokenUsageReporter

reporter = CloudWatchTokenUsageReporter(
    namespace="openai_token_usage",
    dimensions={"project": "my_test_project"}
)
handler = OpenAITokenUsageCallbackHandler(reporter)

llm = ChatOpenAI(model="gpt-4", callbacks=[handler])
prompt = PromptTemplate.from_template("1 + {number} = ")

chain = LLMChain(llm=llm, prompt=prompt)
chain.run(number=2)
```

The above code will perform a single call to an OpenAI GPT-4 backed LLM model, and send token usage metrics and cost estimation to CloudWatch. You can define the desired namespace of your CloudWatch metrics, and add arbitrary metrics dimensions as `str -> str` mapping.

## Contributing

Contributions are very welcome.
To learn more, see the [Contributor Guide].

## License

Distributed under the terms of the [MIT license][license],
_Langchain Token Usage_ is free and open source software.

## Issues

If you encounter any problems,
please [file an issue] along with a detailed description.

## Credits

This project was generated from [@cjolowicz]'s [Hypermodern Python Cookiecutter] template.

[@cjolowicz]: https://github.com/cjolowicz
[pypi]: https://pypi.org/
[hypermodern python cookiecutter]: https://github.com/cjolowicz/cookiecutter-hypermodern-python
[file an issue]: https://github.com/mrtj/langchain-token-usage/issues
[pip]: https://pip.pypa.io/

<!-- github-only -->

[license]: https://github.com/mrtj/langchain-token-usage/blob/main/LICENSE
[contributor guide]: https://github.com/mrtj/langchain-token-usage/blob/main/CONTRIBUTING.md
