from langchain_openai import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
from langchain.output_parsers import OutputFixingParser


PROMPT = """
### INSTRUCTIONS ###
Given the following guidelines, please optimize the provided query for an LLM. 
{format_instructions}

## NOTE ## 
Your task is not to respond to the query to optimize, but to refine it based on the given guidelines. 
Add newlines to the optimized query as needed.

### INPUTS ###

## GUIDELINES ##
```plaintext
{guidelines}
```

## QUERY TO OPTIMIZE ##
```plaintext
{prompt_to_optimize}
```
""".strip()

GUIDELINES = """
Here are some key principles and best practices for prompt engineering with large language models:

1. Give Clear Instructions:
- Provide detailed, step-by-step instructions on the task you want the model to perform
- Make the instructions clear, specific, and unambiguous
- Define constraints or format requirements for the desired output

2. Use Examples/Few-Shot Prompting:
- Include a few examples of inputs and expected outputs in the prompt
- Examples help demonstrate the task and show the model patterns to follow
- Use varied examples to cover different cases and edge conditions

3. Add Relevant Context:
- Provide necessary context or background information the model needs
- Context helps the model better understand constraints and generate more relevant outputs

4. Use Input/Output Prefixes:
- Add prefixes to demarcate different components (instructions, input, output, examples)
- Prefixes provide semantic signals to the model

5. Let Model Complete Partial Inputs:
- Provide a partial input and let the model complete or extend it
- Can be easier than describing the entire task

6. Break Down Complex Tasks:
- Split complex tasks into sequences of simpler prompts
- Chain prompts so output of one becomes input to the next
- Aggregate parallel subtask outputs into the final output

7. Experiment with Parameters:
- Temperature: Higher for more diversity, lower for more grounded outputs
- Top-k/Top-p: Higher for more randomness, lower for deterministic sampling
- Vary parameters to see what works best for your use case

8. Iterative Refinement:
- Prompt engineering requires extensive testing and iteration
- Try rephrasing prompts, using analogous tasks, reordering components
- Increase temperature if getting "safeguarded" responses

9. Test Systematically:
- Define clear benchmarks and success criteria
- Create a test suite with representative examples 
- Measure outputs against gold-standard answers

The key is writing prompts that provide clear guidance to the model while leveraging its capabilities. It often takes
 iterative refinement to find optimal prompts for each specific use case. 
 Systematic testing against benchmarks is crucial.  
"""


class App:
    def __init__(self) -> None:
        self.__key: str | None = None
        self.__client: ChatOpenAI | None = None

    @property
    def key(self) -> str:
        return self.__key

    @key.setter
    def key(self, value: str):
        value = value.strip()
        assert value is not None, "The API key cannot be None."
        assert isinstance(value, str), "The API key must be a string."
        assert len(value) > 0, "The API key cannot be an empty string."

        self.__key = value
        self.__client = ChatOpenAI(api_key=self.__key,
                                   model_name="gpt-4",
                                   temperature=.2,
                                   max_tokens=2000,
                                   max_retries=3)

    def run(self, prompt: str) -> dict:
        # Try three times to run the prompt
        for _ in range(3):
            try:
                return self._run(prompt=prompt)
            except Exception as e:
                print(e)

        return {
            "status": "error",
            "message": "An unexpected error occurred. Please try again later."
        }

    def _run(self, prompt: str) -> dict:
        assert prompt is not None, "The prompt cannot be None."
        assert isinstance(prompt, str), "The prompt must be a string."
        assert len(prompt) > 0, "The prompt cannot be an empty string."
        assert len(prompt.split()) <= 2500 * 4 / 3, f"The prompt cannot exceed {2500 * 4 / 3} words."

        chain: LLMChain = self._build_chain()
        assert chain is not None, "Internal error: 7."

        response = chain.invoke(input={
            "prompt_to_optimize": prompt,
        })

        assert response is not None
        assert response["text"] is not None

        response = response["text"]
        return {
            "status": "success",
            "optimized_prompt": response["optimized_prompt"],
            "required_info": response["required_info"],
        }

    def _build_chain(self) -> LLMChain:
        # NOTE: Experimental, remove later
        optimizer_output_parser = StructuredOutputParser(response_schemas=[
            ResponseSchema(name="optimized_prompt",
                           description="This is the optimized prompt that was generated by following the guidelines."),
            ResponseSchema(name="required_info",
                           description="This is the additional information that was required to optimize the prompt. "
                                       "If no additional information was required, respond by saying 'No additional "
                                       "information was required.'."),
        ])

        optimizer_format_instructions = optimizer_output_parser.get_format_instructions()

        optimizer_output_parser = OutputFixingParser.from_llm(parser=optimizer_output_parser, llm=self.__client)
        optimizer_prompt = PromptTemplate(
            template=PROMPT,
            input_types={
                "format_instructions": str,
                "guidelines": str,
                "prompt_to_optimize": str
            },
            input_variables=["prompt_to_optimize"],
            partial_variables={
                "format_instructions": optimizer_format_instructions,
                "guidelines": GUIDELINES
            },
            output_parser=optimizer_output_parser
        )

        optimizer_chain = LLMChain(
            llm=self.__client,
            output_parser=optimizer_output_parser,
            prompt=optimizer_prompt
        )

        return optimizer_chain
