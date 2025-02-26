from openai import OpenAI
import toml
import streamlit as st


try:
    data = toml.load("api_keys.toml")
    OPENAI_API_KEY= data['OPENAI_API_KEY']
except:
    OPENAI_API_KEY = st.secrets['OPENAI_API_KEY']

def gpt_response(prompt, model = 'gpt-4o-mini',max_tokens = 4000,response_format = "text", temperature=0.5,system_message="you are a helpful assistant"):
    """Standard function for generating a GPT response

    Params:
        prompt (str): Your input prompt
        model (str): GPT Model to use. Default is gpt-3.5-turbo-1106
        max_tokens (str): Max number of tokens to generate. Default is 40000
        response_format (str): Format for the output. Should be either "text" or "json_object". JSON object only availble for 1106 models (GPT-4 Turbo and GPT-3.5 Turbo 1106)
        temperature (float): Randomness of the response.
        system_message (str): Optional system message.

    Output:
        result (str): GPT response text
    """
    client = OpenAI(api_key=OPENAI_API_KEY)
    response = client.chat.completions.create(
        temperature = temperature,
        model=model,
        max_tokens = max_tokens,
        response_format={ "type": response_format },
        messages=[
            {"role": "system", "content": system_message},
            {
                "role": "user",
                "content": f"{prompt}"
            }
        ]
    )
    result = response.choices[0].message.content

    return result


