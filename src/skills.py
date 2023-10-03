"""
Created by Alejandro Cuevas
(t-alejandroc@microsoft.com / acuevasv@andrew.cmu.edu)
August 2023
"""


import asyncio

import semantic_kernel as sk
import semantic_kernel.connectors.ai.open_ai as sk_oai

from models import AIModel
import prompts
import utils

import os

from dotenv import load_dotenv

load_dotenv()


logger = utils.setup_logger(__name__)

## LOAD SEMANTIC KERNEL AND SKILLS START ##
(
    OPENAI_API_KEY,
    AZ_OPENAI_API_KEY,
    AZURE_ENDPOINT,
    PERSONAL_KEY,
    API_KEY_TYPE,
) = utils.get_api_credentials()
ORG_ID = None

logger.info("Endpoint: %s", AZURE_ENDPOINT)
assert (
    OPENAI_API_KEY is not None
    or AZ_OPENAI_API_KEY is not None
    or AZURE_ENDPOINT is not None
), "No OpenAI API key found. Please set the OPENAIAPIKEY environment variable."

logger.info("Key Type: %s", API_KEY_TYPE)
assert (
    API_KEY_TYPE is not None
), "No API key type specified. Please set the APIKEYTYPE environment variable."

kernel = sk.Kernel()
kernel_4 = sk.Kernel()

if API_KEY_TYPE == "openai":
    kernel.add_chat_service(
        "gpt-3.5-turbo",
        sk_oai.OpenAIChatCompletion("gpt-3.5-turbo", OPENAI_API_KEY, ORG_ID),
    )
elif API_KEY_TYPE == "azure":
    kernel.add_chat_service(
        "azure-gpt-35-turbo",
        sk_oai.AzureChatCompletion("gpt-35-turbo", AZURE_ENDPOINT, AZ_OPENAI_API_KEY),
    )
    # kernel.add_chat_service('azure-gpt-4', sk_oai.AzureChatCompletion('gpt-4', AZURE_ENDPOINT, AZ_OPENAI_API_KEY))
elif API_KEY_TYPE == "personal":
    kernel.add_chat_service(
        "gpt-3.5-turbo",
        sk_oai.OpenAIChatCompletion("gpt-3.5-turbo", PERSONAL_KEY, ORG_ID),
    )


# new skills
prober_depersonalized_skill = kernel.create_semantic_function(
    prompts.PROBER_PROMPT_DEPERSONALIZED_FEWSHOT, max_tokens=300, temperature=0.5
)
active_listener_global_skill = kernel.create_semantic_function(
    prompts.ACTIVE_LISTENER_GLOBAL, max_tokens=2000
)


try:
    logger.info("Starting LLM modules...")

    prober_depersonalized = AIModel(
        "prober_depersonalized", kernel, prober_depersonalized_skill
    )
    prober_depersonalized.context["history"] = ""

    global_active_listener = AIModel(
        "global_active_listener", kernel, active_listener_global_skill
    )
    global_active_listener.context["history"] = ""

    logger.info("LLM modules started...")
except Exception as e:
    logger.error("Error:", e)


def get_new_global_vars():
    try:
        api_retry_delay = int(os.environ.get("API_RETRY_DELAY"))
        api_retries = int(os.environ.get("API_RETRIES"))
        api_retry_func = os.environ.get("API_RETRY_FUNC")
    except Exception as e:
        logger.error("Error:", e)
        api_retry_delay = 5
        api_retries = 6
        api_retry_func = "expo"
    return api_retry_delay, api_retries, api_retry_func


MAX_API_TIMEOUT = 60

## LOAD SEMANTIC KERNEL AND SKILLS END
# @backoff.on_exception(backoff.constant, Exception, max_tries=5, interval=0.5)
async def get_module_response(module_name, no_api_calls=False):
    logger.warning(f"Attempting API call for module: '{module_name}'")
    if no_api_calls:
        return "We invoked {}".format(module_name)
    response = None
    if module_name == "prober_depersonalized":
        response = await asyncio.wait_for(
            prober_depersonalized.skill.invoke_async(
                context=prober_depersonalized.context
            ),
            timeout=MAX_API_TIMEOUT,
        )
    elif module_name == "global_active_listener":
        response = await asyncio.wait_for(
            global_active_listener.skill.invoke_async(
                context=global_active_listener.context
            ),
            timeout=MAX_API_TIMEOUT,
        )
        print(response)
        print(response.result)

    try:
        logger.info(
            "Module name: {} | Response: {}".format(module_name, response.result)
        )
        return response.result
    except Exception as e:
        logger.error("Error: {}".format(e))
        return "Faced an error in get_module_response()"


if __name__ == "__main__":
    """
    import time
    for i in range(100):
         response= asyncio.run(global_active_listener.skill.invoke_async(context=global_active_listener.context))
         response = response.result
         print(response)
         time.sleep(1.5)
    """
    print(get_new_global_vars()[2])
    pass
