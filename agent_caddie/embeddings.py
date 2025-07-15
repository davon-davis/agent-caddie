import openai

def get_embedding(text: str) -> list[float]:
    resp = openai.embeddings.create(
      model="text-embedding-ada-002",
      input=text
    )
    return resp.data[0].embedding
