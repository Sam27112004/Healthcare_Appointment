import httpx
import asyncio

async def main():
    async with httpx.AsyncClient() as client:
        # Register a new user
        reg_data = {
            'email': 'new_patient_test2@example.com',
            'password': 'TestPass123!',
            'full_name': 'Test Patient'
        }
        reg_res = await client.post('http://localhost:8000/api/v1/auth/register', json=reg_data)
        if 'access_token' in reg_res.json():
            token = reg_res.json()['access_token']
        else:
            print("Register failed:", reg_res.json())
            return
            
        doc_res = await client.get('http://localhost:8000/api/v1/doctors', headers={'Authorization': f'Bearer {token}'})
        print('DOCTORS RESP:', doc_res.status_code, doc_res.json())

asyncio.run(main())
