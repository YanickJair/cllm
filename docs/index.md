<p align="center" style="margin: 0 0 10px">
  <img width="350" height="208" src="https://raw.githubusercontent.com/YanickJar/cllm/master/docs/img/clm-logo.png" alt='CLM'>
</p>

<h1 align="center" style="font-size: 3rem; margin: -15px 0">
CLM
</h1>

---

<div align="center">
<p>
<a href="https://github.com/encode/httpx/actions">
    <img src="https://github.com/encode/httpx/workflows/Test%20Suite/badge.svg" alt="Test Suite">
</a>
<a href="https://pypi.org/project/clm/">
    <img src="https://badge.fury.io/py/httpx.svg" alt="Package version">
</a>
</p>

<em>A next-generation HTTP client for Python.</em>
</div>

CLM is a natural language and structural information compressor for LLM. It compresses by preserving the semantic
meaning of the content information thus providing equal or better response from LLM while reducing cost and response time.
---

Install HTTPX using pip:

```shell
$ pip install clm
```

Now, let's get started:
```pycon
>>> from clm import CLMConfig, CLMEncoder
>>> cfg = CLMConfig(lang="en")
>>> encoder = CLMEncoder(cfg=cfg)
>>> result = encoder.encode("You are a Prompt Compressor Agent, your job is to analyse invoice documents", verbose=True)
>>> result.compressed
[REQ:ANALYZE] [TARGET:DOCUMENTS]  ...
```
