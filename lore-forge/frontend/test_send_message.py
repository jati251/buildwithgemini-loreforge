from a2a.types.a2a_pb2 import SendMessageRequest
from a2a.types import Message, Role, Part

msg = Message(
    message_id="123",
    role=Role.ROLE_USER,
    parts=[Part(text="hello")]
)
req = SendMessageRequest(message=msg)
print(req)
