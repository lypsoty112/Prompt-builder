
# Prompt-builder

Prompt Builder is a small Python application that implements the principles outlined in the paper "[Principled Instructions Are All You Need for Questioning LLaMA-1/2, GPT-3.5/4](https://arxiv.org/abs/2312.16171)". It allows users to generate natural language prompts adhering to specific rules and guidelines defined in the paper.

## Usage

Simply past the prompt you want to optimize in the text box and click the "Optimize" button. The application will then generate a prompt that adheres to the guidelines outlined in the paper.

## Installation

Either use the [online version](https://promptbuilder.streamlit.app/),  or go to the [GitHub](https://github.com/lypsoty112/Prompt-builder) and download the repository.

### Repository installation

Install the repository's packages using  

```bash
pip install -r requirements.txt
```

_(Optional): Set your API key in a_ `.env`_file as seen in the_ `.env.template` _file._

Then, run the project using

```bash
streamlit run main.py
```
