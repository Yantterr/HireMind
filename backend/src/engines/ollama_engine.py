from dataclasses import asdict

import httpx

from src.config import settings
from src.dto.chats_dto import MessageDataclass
from src.models.chats_models import NNResponseModel
from src.models.generally_models import NNRoleEnum


async def ollama_request(messages: list[MessageDataclass]) -> NNResponseModel:
    """Send a request to the Ollama engine and return the response."""
    ollama_context = [
        {key: value for key, value in asdict(message).items() if key in ('role', 'content')} for message in messages
    ]
    ollama_url = settings.ollama_url

    payload = {
        'model': settings.ollama_model,
        'options': {
            'num_ctx': 65536,
        },
        'messages': ollama_context,
        'stream': False,
        'think': False,
    }

    async with httpx.AsyncClient(timeout=3600) as client:
        response = await client.post(ollama_url, json=payload)
        data = response.json()

    return NNResponseModel(
        count_request_tokens=data['prompt_eval_count'],
        count_response_tokens=data['eval_count'],
        role=NNRoleEnum.ASSISTANT,
        content=data['message']['content'],
    )
