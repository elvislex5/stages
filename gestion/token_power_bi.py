import requests

def generate_embed_token():
    url = "https://login.microsoftonline.com/YOUR_TENANT_ID/oauth2/v2.0/token"
    data = {
        "grant_type": "client_credentials",
        "client_id": "YOUR_CLIENT_ID",
        "client_secret": "YOUR_CLIENT_SECRET",
        "scope": "https://analysis.windows.net/powerbi/api/.default",
    }
    response = requests.post(url, data=data)
    token = response.json().get("access_token")
    return token
