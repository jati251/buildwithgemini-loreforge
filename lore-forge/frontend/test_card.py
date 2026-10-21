import asyncio
import httpx
import google.auth
import google.auth.transport.requests
from a2a.client import ClientFactory, ClientConfig
from a2a.types import AgentCard, Message, Role, Part
from a2a.types.a2a_pb2 import SendMessageRequest, SendMessageConfiguration

async def test():
    creds, _ = google.auth.default(scopes=["https://www.googleapis.com/auth/cloud-platform"])
    creds.refresh(google.auth.transport.requests.Request())
    headers = {"Authorization": f"Bearer {creds.token}", "Content-Type": "application/json"}
    
    A2A_BASE = "https://us-east1-aiplatform.googleapis.com/reasoningEngines/v1/projects/196272355734/locations/us-east1/reasoningEngines/3066646781518413824/api/a2a/app"
    
    async with httpx.AsyncClient(headers=headers, timeout=120) as client:
        resp = await client.get(f"{A2A_BASE}/.well-known/agent-card.json")
        card = AgentCard()
        from google.protobuf.json_format import ParseDict
        ParseDict(resp.json(), card, ignore_unknown_fields=True)
        interface = card.supported_interfaces.add()
        interface.protocol_binding = "http_json"
        interface.url = A2A_BASE
        
        factory = ClientFactory(ClientConfig(httpx_client=client))
        a2a_client = factory.create(card)
        
        msg = Message(message_id="123", role=Role.ROLE_USER, parts=[Part(text="hello")])
        req = SendMessageRequest(message=msg, configuration=SendMessageConfiguration(return_immediately=False))
        
        try:
            async for event in a2a_client.send_message(req):
                print(event)
        except Exception as e:
            print(f"Exception calling a2a_client: {type(e).__name__}: {e}")

asyncio.run(test())
