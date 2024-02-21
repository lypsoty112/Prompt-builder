
from langchain_openai import OpenAI
from langchain.chains import LLMChain
from langchain.prompts import PromptTemplate
from langchain.output_parsers import StructuredOutputParser, ResponseSchema
import json
import os
import traceback


class App:
    def __init__(self) -> None:
        self.__key: str = None
        self.__client: OpenAI = None
    
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
        self.__client = OpenAI(api_key=self.__key, temperature=.7, max_tokens=1500, max_retries=3)

    def run(self, prompt: str) -> dict:
        try: 
            return self._run(prompt=prompt)
        except Exception as e:
            return {
                "status": "error",
                "message": str(e) + ": " + traceback.format_exc() if os.getenv("logging", "INFO") == "DEBUG" else str(e)
            }
    def _run(self, prompt: str) -> dict:
        assert prompt is not None, "The prompt cannot be None."
        assert isinstance(prompt, str), "The prompt must be a string."
        assert len(prompt) > 0, "The prompt cannot be an empty string."
        assert len(prompt.split()) <= 2500 * 4/3, f"The prompt cannot exceed {2500 * 4/3} words."


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
        prompt = """
### INSTRUCTIONS ###
Given the following guidelines, please optimize the provided query for an LLM. 
## NOTE ## 
Your task is not to respond to the query to optimize, but to refine it based on the given guidelines. 
{format_instructions}

### INPUTS ###

## GUIDELINES ##
```plaintext
{guidelines}
```

## QUERY TO OPTIMIZE ##
```plaintext
{prompt_to_optimize}
```

"""
        guidelines = """
1. Be Concise:
    - Avoid politeness in your query.
    - Get straight to the point.

2. Audience Integration:
    - Make sure your query mentions the intended audience for the response. 

3. Affirmative Directives:
    - Use affirmative language like 'do'.
    - Avoid negatives like 'don't'.
    - Example: "Don't forget to..." becomes "Remember to..."

4. Clarity Prompt:
    - When asking for clarification about a certain topic, use 1 of the following formats:
        - "Explain [TOPIC] in simple terms."
        - "Explain to me like I'm a beginner in [FIELD]"
        - "Write your answer using simple language like you're explaining something to a 5-year-old."
        - Add "Explain to me like I'm 11 years old." at the end of the query.

5. Tip Incentive:
    - Offer a tip for better solutions.
    - Example: "I'll tip $xxx for a better solution."

6. Example-Driven Querying:
    - Use examples for clarity when applicable.

7. Formatting:
    - When formatting your query, start with ‘###Instruction###’, followed by either ‘###Example###’ or ‘###Question###’ if relevant. Subsequently, present your content. Use one or more line breaks to separate instructions, examples, questions, context, and input data.

8. Task and Requirement:
    - Incorporate the following phrases: 
        - "Your task is to..."
        - "You MUST..."

9. Penalization Warning:
    - Incorporate the following phrases: 
        - "You will be penalized..."

10.Natural Response:
    - Use the phrase "Answer a question given in a natural, human-like manner" in your query.

11. Leading Words:
    - Guide step-by-step thinking.
    - Use leading words like writing "think step by step"

12. Unbiased Response:
    - Add to your query the following phrase "Ensure that your answer is unbiased and avoids relying on stereotypes."

13. Testing Understanding:
    - To inquire about a specific topic or idea or any information and you want to test your understanding, you can use the following phrase: "Teach me any [theorem/topic/rule name] and include a test at the end, and let me know if my answers are correct after I respond, without providing the answers beforehand."

14. Assign Role:
    - Assign a role to the LLM.
    - Example: "Your role is..."

15. Delimiters Usage:
    - Employ delimiters.

16. Repetition:
    -  Repeat a specific word or phrase multiple times within a query.

17. Output Primers:
    - Use output primers, which involve concluding your query with the beginning of the desired output. Utilize output primers by ending your prompt with the start of the anticipated response.

18. Detailed Content:
    - To write an essay /text /paragraph /article or any type of text that should be detailed: "Write a detailed [essay/text /paragraph] for me on [topic] in detail by adding all the information necessary".

19. Text Correction:
    - To correct/change specific text without changing its style: "Try to revise every paragraph sent by users. You should only improve the user’s grammar and vocabulary and make sure it sounds natural. You should maintain the original writing style, ensuring that a formal paragraph remains formal."

20. Complex Coding Query:
    - When you have a complex coding query that may be in different files: "From now and on whenever you generate code that spans more than one file, generate a [programming language ] script that can be run to automatically create the specified files or make changes to existing files to insert the generated code. [your question]".

21. Initiate or Continue Text:
    - When you want to initiate or continue a text using specific words, phrases, or sentences, utilize the following query: "I’m providing you with the beginning [song lyrics/story/paragraph/essay...]: [Insert lyrics/words/sentence]. Finish it based on the words provided. Keep the flow consistent."

22. Clear Requirements:
    - Clearly state the requirements that the model must follow in order to produce content, in the form of the keywords, regulations, hint, or instructions

23. Text Similarity:
    - To write any text, such as an essay or paragraph, that is intended to be similar to a provided sample, include the following instructions: "Use the same language based on the provided paragraph[/title/text /essay/answer]".
        """
        
        optimizer_output_parser = StructuredOutputParser(response_schemas=[
            ResponseSchema(name="optimized_prompt", description="This is the optimized prompt that was generated by following the guidelines."),
            ResponseSchema(name="required_info", description="This is the additional information that was required to optimize the prompt. If no additional information was required, respond by saying 'No additional information was required.'."),
        ])
        
        optimizer_format_instructions = optimizer_output_parser.get_format_instructions()
        optimizer_prompt = PromptTemplate(
            template=prompt,
            input_types={
                "format_instructions": str,
                "guidelines": str,
                "prompt_to_optimize": str
            },
            input_variables=["prompt_to_optimize"],
            partial_variables={
                "format_instructions": optimizer_format_instructions,
                "guidelines": guidelines
            },
            output_parser=optimizer_output_parser
        )

        optimizer_chain = LLMChain(
            llm=self.__client,
            output_parser=optimizer_output_parser,
            prompt=optimizer_prompt
        )

        return optimizer_chain