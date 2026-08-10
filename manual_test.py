import asyncio
import httpx
import time

async def run_test():
    print("🚀 Starting Profile Intelligence Engine test...")
    
    # The payload matching PipelineInput schema
    payload = {
        "cv_text": "Senior Machine Learning Engineer with 10 years of experience in Python and PyTorch. Built scalable APIs.",
        "rate_desired": 120.0
    }
    
    async with httpx.AsyncClient(base_url="http://127.0.0.1:8000") as client:
        # 1. Trigger the analysis
        print("📨 Submitting CV to /analyze endpoint...")
        response = await client.post(
            "/analyze", 
            json=payload,
            params={"niche": "ai-ml-engineer", "version": "1.0"},
            follow_redirects=False
        )
        
        if response.status_code != 303:
            print(f"❌ Failed to start analysis. Status: {response.status_code}")
            print(response.text)
            return

        # FastAPI RedirectResponse sets the Location header
        status_url = response.headers.get("location")
        run_id = status_url.split("/")[2]
        print(f"✅ Analysis started! Run ID: {run_id}")
        
        # 2. Poll the status endpoint
        while True:
            status_response = await client.get(status_url)
            if status_response.status_code != 200:
                print(f"❌ Error polling status: {status_response.text}")
                break
                
            status_data = status_response.json()
            stage = status_data.get("stage")
            progress = status_data.get("progress_pct", 0)
            print(f"⏳ Status: {stage} ({progress}%)")
            
            if status_data.get("finished_at"):
                if status_data.get("error"):
                    print(f"❌ Pipeline failed: {status_data['error']}")
                else:
                    print("✅ Pipeline completed successfully!")
                break
                
            await asyncio.sleep(1)
            
        # 3. Fetch the final result
        print("\n📊 Fetching final generated result...")
        result_url = f"/analyze/{run_id}/result"
        result_response = await client.get(result_url)
        
        import json
        print("\n✨ Final Result:")
        print(json.dumps(result_response.json(), indent=2))

if __name__ == "__main__":
    asyncio.run(run_test())
