from a2a.types import AgentCard

card = AgentCard()
print(f"Supported interfaces initially: {card.supported_interfaces}")
try:
    from a2a.types import AgentInterface, TransportProtocol
    # Add HTTP JSON interface
    interface = card.supported_interfaces.add()
    interface.transport = 2  # http_json
    interface.url = "https://example.com/api"
    print(f"Supported interfaces modified: {card.supported_interfaces}")
except Exception as e:
    print(f"Error modifying interface: {e}")
