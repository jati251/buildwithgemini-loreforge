from a2a.client import ClientConfig, ClientFactory
from a2a.types import AgentCard

card = AgentCard()
try:
    factory = ClientFactory(ClientConfig())
    client = factory.create(card)
    print("Created client from empty card.")
except Exception as e:
    print(f"Error creating client: {e}")
