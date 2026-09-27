from laya import Router
import json

print("Loading Laya model")
router = Router(preload=True, device="cuda")

security_state = """
Subject: URGENT: Unusual Login Attempt Detected
From: security-alert@microsoft-verify-update.com
Body: Dear User, we detected a login from an unknown IP in Nepal. 
Your account will be locked in 24 hours. Click here immediately to verify your identity: http://bit.ly/secure-ms-login-xyz
Failure to act will result in permanent data loss.
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
    "urgency_level": {
        "type": "score",
        "instructions": "How urgent is the required response based on the text?",
        "criteria": [
            "0: Low (No immediate action needed)", 
            "1: Medium (Review within 24h)", 
            "2: High (Immediate action required / threats of loss)"
        ]
    },
    "contains_suspicious_link": {
        "type": "noul",
        "instructions": "Does the message contain a suspicious, shortened, or obfuscated URL?"
    }
}

print("🛡️ Analyzing security state with Laya...\n")

result = router.predict(security_state, questions)
answers = result["answers"]

print("✅ Analysis Complete!")
print(f"Threat Category      : {answers['threat_category']['choice'].upper()} (Confidence: {answers['threat_category']['confidence']:.2f})")
print(f"Urgency Score        : {answers['urgency_level']['score']} / 2.0")
print(f"Suspicious Link      : {'YES' if answers['contains_suspicious_link']['noul'] > 0.5 else 'NO'} (Probability: {answers['contains_suspicious_link']['noul']:.2f})")
