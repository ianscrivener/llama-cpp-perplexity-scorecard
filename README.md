# llama.cpp perplexity scorecard

A helper project to run perplexity tests for **[llama.cpp](https://github.com/ggerganov/llama.cpp)**

[Perplexity](https://en.wikipedia.org/wiki/Perplexity) is the most commonly used measure of a language model's performance on a given text corpus. It is a measure of how well a model is able to predict the contents of a dataset. **Lower perplexity scores are better**.`llama.cpp` includes a perplexity self test binary`./perplexity`.

See background discussions in the [llama.cpp discussions](https://github.com/ggerganov/llama.cpp/discussions) on the needs and motives for this project [here](https://github.com/ggerganov/llama.cpp/discussions/1985) and [here](https://github.com/ggerganov/llama.cpp/discussions/406)

This xxx uploads perplexity scores and test results to an Amazon S3 bucket for analysis and checking the (coming soon) **llama.cpp perplxity leaderboard**.

### Install
```
pip install -r requirements.txt
```


### Running
```
python3 perplexity_scorecard.py
```



---

