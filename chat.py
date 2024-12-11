import logging
import os
from time import sleep

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import BaseModel


load_dotenv()

OPENAI_KEY = os.environ['OPENAI_KEY']
OPENAI_MODEL = os.environ['OPENAI_MODEL']


class Story(BaseModel):
    source: str
    story: str


class Response(BaseModel):
    stories: list[Story]


def generate_stories_openai(user_input, temperature=0.8, frequency_penalty=0.2, presence_penalty=0, max_retry=3):
    messages = [
        {
            'role': 'system',
            'content': [
                {
                    'type': 'text',
                    'text': '''
                        You are a news expert, writer and a podcast expert.
                        Your task is to write bite sized news stories that are easy to read 
                        and convey to an audience for a podcast host from the data given by the user.
                        Each news article in the data consists of a headline, an excerpt and the source it is from.
                        For each article write a story based on the headline and the excerpt.
                        Do not translate the data to a different language.
                    '''
                }
            ]
        },
        {
            'role': 'user',
            'content': [
                {
                    'type': 'text',
                    'text': user_input
                }
            ]
        }
    ]

    client = OpenAI(api_key=OPENAI_KEY)

    for i in range(max_retry):
        try:
            completion = client.beta.chat.completions.parse(
                model=OPENAI_MODEL,
                temperature=temperature,
                frequency_penalty=frequency_penalty,
                presence_penalty=presence_penalty,
                messages=messages,
                response_format=Response
            )
            chat_response = completion.choices[0].message.content
            return chat_response
        except Exception as e:
            if i == max_retry - 1:
                return ''
            logging.exception(f'Error: {e}')
            sleep(1)


def translate_openai(text, lang='spanish', temperature=0.8, frequency_penalty=0.2, presence_penalty=0, max_retry=3):
    messages = [
        {
            'role': 'system',
            'content': [
                {
                    'type': 'text',
                    'text': f'''
                        You are a helpful ai agent, designed to translate text to the {lang} language.
                        Respond with the translated text, without any comments or any extra text besides the translation.
                    '''
                }
            ]
        },
        {
            'role': 'user',
            'content': [
                {
                    'type': 'text',
                    'text': text
                }
            ]
        }
    ]

    client = OpenAI(api_key=OPENAI_KEY)

    for i in range(max_retry):
        try:
            completion = client.chat.completions.create(
                model=OPENAI_MODEL,
                temperature=temperature,
                frequency_penalty=frequency_penalty,
                presence_penalty=presence_penalty,
                messages=messages,
            )
            chat_response = completion.choices[0].message.content
            return chat_response
        except Exception as e:
            if i == max_retry - 1:
                return ''
            logging.exception(f'Error: {e}')
            sleep(1)
