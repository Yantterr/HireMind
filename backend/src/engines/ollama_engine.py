import httpx

import src.utils.gpt_utils as gpt_utils
from src.config import settings
from src.dataclasses.gpt_dataclasses import MessageDataclass
from src.models.generally_models import NNRoleEnum
from src.models.gpt_models import NNResponseModel


async def ollama_request(messages: list[MessageDataclass]) -> NNResponseModel:
    """Send a request to the Ollama engine and return the response."""
    ollama_context = gpt_utils.ollama_generate_context(messages=messages)
    ollama_url = settings.ollama_url

    payload = {'model': settings.ollama_model, 'messages': ollama_context, 'stream': False, 'think': False}

    async with httpx.AsyncClient(timeout=99999999999999999999999999999) as client:
        response = await client.post(ollama_url, json=payload)
        data = response.json()

    return NNResponseModel(
        count_request_tokens=data['prompt_eval_count'],
        count_response_tokens=data['eval_count'],
        role=NNRoleEnum.ASSISTANT,
        content=data['message']['content'],
    )
