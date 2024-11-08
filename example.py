# Create a human-like response to a prompt
from openai import OpenAI
client = OpenAI()

completion = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "system", "content": "You are a helpful assistant."},
        {
            "role": "user",
            "content": "who are you?."
        }
    ]
)

print(completion.choices[0].message)

#--------------------------------------------------------------------------------------------------
# Generate an image based on a textual prompt
# from openai import OpenAI
# client = OpenAI()

# response = client.images.generate(
#     prompt="A cute baby sea otter",
#     n=2,
#     size="1024x1024"
# )

# print(response.data[0].url)

#------------------------------------------------------------------------------------------------
# Create vector embeddings for a string of text
# from openai import OpenAI
# client = OpenAI()

# response = client.embeddings.create(
#     model="text-embedding-3-large",
#     input="The food was delicious and the waiter..."
# )

# print(response)