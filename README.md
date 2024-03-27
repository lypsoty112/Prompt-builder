
# Prompt-builder

Prompt Builder is a small Python application that generates natural language prompts based on documentation and best practices from [OpenAI](https://platform.openai.com/docs/guides/prompt-engineering), Google (https://ai.google.dev/docs/prompt_best_practices & https://developers.google.com/machine-learning/resources/prompt-eng), [Anthropic](https://docs.anthropic.com/claude/docs/prompt-engineering), [Cohere](https://docs.cohere.com/docs/crafting-effective-prompts), and other leading AI companies. It utilizes GPT-4 to generate prompts adhering to specific rules and guidelines.
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
