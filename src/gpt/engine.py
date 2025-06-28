from openai import OpenAI

from config import settings
from src.gpt.models import NNContext_model, NNMessage_model, NNResponse_model

NNClient = OpenAI(api_key=settings.gpt_api_key)


def create_nn_request(message: NNMessage_model, context: NNContext_model) -> NNResponse_model:
    """Create NN request."""
    context.append(message)
    res = NNClient.responses.create(model='gpt-4o', messages=context, max_output_tokens=20, temperature=0.5)
    return {
        'request_tokens': res.usage.prompt_tokens,
        'response_tokens': res.usage.completion_tokens,
        'message': message.content,
        'result': res.choices[0].message.content,
    }
