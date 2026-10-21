import httpx
import asyncio

async def test():
    async with httpx.AsyncClient() as client:
        try:
            resp = await client.post("https://us-east1-aiplatform.googleapis.com/reasoningEngines/v1/projects/196272355734/locations/us-east1/reasoningEngines/3066646781518413824/api/a2a/app")
            print(resp.status_code)
        except Exception as e:
            print(f"Error: {e}")

asyncio.run(test())
