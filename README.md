# llama.cpp perplexity scorecard

A helper project to run perplexity tests for **[llama.cpp](https://github.com/ggerganov/llama.cpp)**. llama.cpp is a leading LLM (Large Language Model) inference engine. llama.cpp runs LLMs like **[Llama2](https://ai.meta.com/llama/)**.

[Perplexity](https://en.wikipedia.org/wiki/Perplexity) is the most commonly used measure of a language model's performance on a given text corpus. It is a measure of how well a model is able to predict the contents of a dataset. **Lower perplexity scores are better**.

See background discussions in the [llama.cpp discussions](https://github.com/ggerganov/llama.cpp/discussions) on the needs and motives for this project [here](https://github.com/ggerganov/llama.cpp/discussions/1985) and [here](https://github.com/ggerganov/llama.cpp/discussions/406)

This python app wraps the **llama.cpp** `./perplexity` executable and uploads perplexity scores and test results as JSON to an Amazon S3 bucket for analysis.

Coming soon... the **llama.cpp perplexity leaderboard** and Jupyter (.ipynb) analysis samples.

### Install
```
pip install -r requirements.txt
```


### Run
```
python3 perplexity_scorecard.py
```



