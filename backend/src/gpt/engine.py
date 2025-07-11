from datetime import datetime

from openai import OpenAI

from src.config import settings
from src.gpt.dataclassees import Chat, GptResponse

NNClient = OpenAI(api_key=settings.gpt_api_key)


def create_gpt_request(chat: Chat) -> GptResponse:
    """Create NN request."""
    if not chat.messages or len(chat.messages) == 0:
        raise ValueError('Chat messages cannot be empty')

    return GptResponse(
        request_tokens=1,
        response_tokens=1,
        result='Test response',
        created_at=datetime.now(),
    )

    # res = NNClient.chat.completions.create(
    #     model='gpt-4o',
    #     messages=chat['messages'],
    #     max_tokens=100,
    #     top_p=0.9,
    #     temperature=0.8,
    # )
    # if not res.usage or not res.choices or res.choices[0].message.content is None:
    #     raise ValueError('No usage data in the response from the neural network')

    # return GptResponseModel(
    #     request_tokens=res.usage.prompt_tokens,
    #     response_tokens=res.usage.completion_tokens,
    #     result=res.choices[0].message.content,
    #     created_at=datetime.now().isoformat(timespec='seconds'),
    # )
