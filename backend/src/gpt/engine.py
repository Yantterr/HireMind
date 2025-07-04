from datetime import datetime

from openai import OpenAI

from src.config import settings
from src.gpt.models import GptResponseModel

NNClient = OpenAI(api_key=settings.gpt_api_key)


def create_gpt_request(chat: dict) -> GptResponseModel:
    """Create NN request."""
    if not chat['messages']:
        raise ValueError('Chat messages cannot be empty')

    return GptResponseModel(
        **{
            'request_tokens': 1,
            'response_tokens': 1,
            'result': 'Test response',
            'created_at': datetime.now().isoformat(timespec='seconds'),
        }
    )
    # res = NNClient.chat.completions.create(
    #     model='gpt-4o',
    #     messages=chat['messages'],
    #     max_tokens=10,
    #     top_p=0.95,
    #     temperature=0.7,
    # )
    # if not res.usage or not res.choices or res.choices[0].message.content is None:
    #     raise ValueError('No usage data in the response from the neural network')

    # return GptResponseModel(
    #     request_tokens=res.usage.prompt_tokens,
    #     response_tokens=res.usage.completion_tokens,
    #     result=res.choices[0].message.content,
    #     created_at=datetime.now().isoformat(timespec='seconds'),
    # )
