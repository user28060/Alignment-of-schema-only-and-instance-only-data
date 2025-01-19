import time

import openai
import torch


def get_embedding_hf(text, tokenizer, model):
    # Tokenize the input text and get the input IDs and attention mask
    inputs = tokenizer(
        text, return_tensors="pt", max_length=512, truncation=True, padding=True
    )
    input_ids = inputs["input_ids"]
    attention_mask = inputs["attention_mask"]
    # Get hidden states from the last layer
    with torch.no_grad():
        outputs = model(input_ids, attention_mask=attention_mask)

    # Pool the hidden states to create a single vector (average pooling)
    embeddings = outputs.last_hidden_state
    # Perform mean pooling to get a single vector for the sentence
    sentence_embedding = torch.mean(embeddings, dim=1).squeeze().numpy()

    return sentence_embedding


def get_embedding_openai(text, model="text-embedding-ada-002", max_retries=3):
    for attempt in range(max_retries):
        try:
            response = openai.Embedding.create(input=[text], model=model)
            if "data" in response and len(response["data"]) > 0:
                return response["data"][0]["embedding"]
            else:
                print("Error: No embedding data found in the response.")
                return None
        except openai.error.RateLimitError as e:
            print(f"Rate limit error: {e}. Retrying in 10 seconds...")
            time.sleep(10)  # Wait longer for rate limits
        except openai.error.Timeout as e:
            print(f"Timeout error: {e}. Retrying in 5 seconds...")
            time.sleep(5)  # Shorter wait for timeouts
        except openai.error.OpenAIError as e:
            print(f"OpenAI error: {e}")
            break  # Break on other OpenAI-related errors
        except Exception as e:
            print(f"Unexpected error: {e}")
            break  # Break on non-OpenAI errors
    return None  # Return None after max_retries
