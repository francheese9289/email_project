import openai
import os
from dotenv import load_dotenv

# Load environment variables from the .env file in the config folder
load_dotenv(dotenv_path='config/.env')

def send_link_to_chatgpt(drive_link, instructions_path):
    api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        raise ValueError("The OPENAI_API_KEY environment variable is not set.")
    
    # Initialize the OpenAI client with the API key
    client = openai.OpenAI(api_key=api_key)
    
    # Read instructions from the file with UTF-8 encoding
    with open(instructions_path, 'r', encoding='utf-8') as file:
        instructions = file.read()
    
    prompt = (
        f"Please assume the content of the CSV file linked below is accessible.\n"
        f"Link to the CSV file: {drive_link}\n\n"
        f"{instructions}\n\n"
        "Process the CSV file according to the instructions and provide the updated CSV content or a summary of changes."
    )
    
    # Create a chat completion request to the OpenAI API
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    
    # Extract the updated CSV link or content from the response
    reply = response.choices[0].message.content
    return reply

# For testing
if __name__ == "__main__":
    drive_link = 'https://drive.google.com/file/d/1f3IYSC45GlL3Js8xSqboZTKMvMw8ZK1K/view?usp=drive_link'
    instructions_path = "instructions.txt"
    print(send_link_to_chatgpt(drive_link, instructions_path))
