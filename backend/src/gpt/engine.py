from openai import OpenAI

from config import settings
from src.gpt.models import ChatModel, GptResponseModel

NNClient = OpenAI(api_key=settings.gpt_api_key)


def create_gpt_request(chat: ChatModel) -> GptResponseModel:
    """Create NN request."""
    res = NNClient.responses.create(model='', messages=chat.messages, max_output_tokens=20)
    return {
        'request_tokens': res.usage.prompt_tokens,
        'response_tokens': res.usage.completion_tokens,
        'message': message.content,
        'result': res.choices[0].message.content,
    }
