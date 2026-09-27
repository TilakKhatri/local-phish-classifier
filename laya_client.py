import requests
import json

# The URL of your local persistent server
LAYA_API_URL = "http://localhost:8000/v1/systemone"

security_state = """
Subject: URGENT: Unusual Login Attempt Detected
From: security-alert@microsoft-verify-update.com
Body: Dear User, we detected a login from an unknown IP in Nepal. 
Your account will be locked in 24 hours. Click here immediately to verify your identity: http://bit.ly/secure-ms-login-xyz
"""

questions = {
    "threat_category": {
        "type": "choice",
        "instructions": "What is the primary security threat category?",
        "criteria": {
            "phishing": "Attempts to steal credentials via deceptive links or urgency",
            "malware": "References to downloading malicious files or executables",
            "spam": "Unsolicited commercial messages with no direct threat",
            "legitimate": "Genuine, expected system notifications"
        }
    },
    "contains_suspicious_link": {
        "type": "noul",
        "instructions": "Does the message contain a suspicious, shortened, or obfuscated URL?"
    }
}

payload = {
    "state": security_state,
    "questions": questions
}

print("Sending request to local Laya server...")
response = requests.post(LAYA_API_URL, json=payload)

if response.status_code == 200:
    result = response.json()
    answers = result["answers"]
    
    print("\n Analysis Complete (Instant!)")
    print(f"Threat Category : {answers['threat_category']['choice'].upper()}")
    print(f"Suspicious Link : {'YES' if answers['contains_suspicious_link']['noul'] > 0.5 else 'NO'}")
else:
    print(f"Error: {response.status_code} - {response.text}")
    
    