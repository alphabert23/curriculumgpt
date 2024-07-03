from openai import OpenAI, AsyncOpenAI
import toml
import requests
from bs4 import BeautifulSoup
import json


data = toml.load("api_keys.toml")

OPENAI_API_KEY= data['OPENAI_API_KEY']
BROWSERLESS_API_KEY = data["BROWSERLESS_API_KEY"]

client = OpenAI(api_key=OPENAI_API_KEY)
async_client = AsyncOpenAI(api_key=OPENAI_API_KEY)

def gpt_response(prompt, model = 'gpt-3.5-turbo-1106',max_tokens = 4000,response_format = "text", temperature=0.5,system_message = "You are a helpful assistant"):
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

def async_gpt_response(prompt, model = 'gpt-3.5-turbo-1106',max_tokens = 4000,response_format = "text", temperature=0.5,system_message = "You are a helpful assistant"):
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
    response = async_client.chat.completions.create(
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

def scrape_website(url: str):
    # scrape website, and also will summarize the content based on objective if the content is too large
    # objective is the original objective & task that user give to the agent, url is the url of the website to be scraped

    # Define the headers for the request
    headers = {
        'Cache-Control': 'no-cache',
        'Content-Type': 'application/json',
    }

    # Define the data to be sent in the request
    data = {
        "url": url
    }

    # Convert Python object to JSON string
    data_json = json.dumps(data)

    # Send the POST request
    post_url = f"https://chrome.browserless.io/content?token={BROWSERLESS_API_KEY}"
    response = requests.post(post_url, headers=headers, data=data_json)

    # Check the response status code
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        text = soup.get_text()

        hyperlinks = [a.get('href') for a in soup.find_all('a', href=True) if 'http' in a.get('href')]

        if len(text) > 50000:
            response = text[:50000]
        
        return response,hyperlinks
    else:
        print(f"HTTP request failed with status code {response.status_code}")

def build(assistant_name, instructions, model, tools, files):

    file_ids = []
    for file in files:
        assistant_file = client.files.create(
            file=file,
            purpose='assistants'
        )
        file_ids.append(assistant_file.id)

    assistant_tools = []
    for tool in tools:
        assistant_tools.append({'type': tool})

    assistant = client.beta.assistants.create(
        name=assistant_name,
        instructions=instructions,
        model=model,
        tools=assistant_tools,
        file_ids=file_ids
    )

    return assistant

def start_thread(assistant_id, initial_message, custom_instructions=None, thread_id=None):
    if thread_id is None:
        thread_id = client.beta.threads.create().id

    client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=initial_message
    )

    assistant_name = client.beta.assistants.retrieve(assistant_id).name

    if custom_instructions is None:
        instructions = f"Please address the user as James."
    else:
        instructions = custom_instructions

    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id,
        instructions=instructions
    )

    status = run.status
    while (status != 'completed'):
        run = client.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run.id
        )
        if status != run.status:
            status = run.status

    messages = client.beta.threads.messages.list(
        thread_id=thread_id
    )
    for x in reversed(messages.data):
        role = x.assistant_id is not None
        if role:
            role = assistant_name
        else:
            role = 'User'
        x_message = f"{role}: {x.content[0].text.value}\n\n"
        print(x_message)

    return run

