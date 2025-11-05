import anthropic

client = anthropic.Anthropic()
#export ANTHROPIC_API_KEY='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'


message = client.messages.create(
    model="claude-sonnet-4-5",
    max_tokens=1000,
    messages=[
        {
            "role": "user",
            "content": "What should I search for to find the latest developments in renewable energy?"
        }
    ]
)
print(message.content)