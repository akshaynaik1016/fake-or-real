from typing import Dict, Any, List

EMERGENCY_INCIDENT_GUIDANCE = {
    "entered_password": {
        "headline": "Credentials Compromise Incident Response",
        "severity": "CRITICAL",
        "caution_note": "Do not reuse the compromised password on any other account. Perform password resets only from the legitimate service's verified URL.",
        "immediate_steps": [
            {
                "order": 1,
                "action": "Change Password Immediately on the Official Website",
                "priority": "CRITICAL",
                "instructions": "Navigate directly to the official legitimate platform by typing the verified URL in your browser. Change your password immediately."
            },
            {
                "order": 2,
                "action": "Terminate All Active Sessions",
                "priority": "CRITICAL",
                "instructions": "In your account security settings, select 'Log out of all other devices' or 'Revoke all sessions' to kick out any active unauthorized sessions."
            },
            {
                "order": 3,
                "action": "Enable Multi-Factor Authentication (MFA)",
                "priority": "HIGH",
                "instructions": "Activate an authenticator app (e.g. Google Authenticator) rather than SMS-based MFA where possible."
            },
            {
                "order": 4,
                "action": "Check for Password Reuse",
                "priority": "HIGH",
                "instructions": "If you used this same password on your email, banking, or social media accounts, update those accounts immediately with unique passwords."
            }
        ]
    },
    "entered_card": {
        "headline": "Payment Card Data Exposure Protocol",
        "severity": "CRITICAL",
        "caution_note": "Do not attempt to contact numbers listed on the suspicious website. Contact your bank exclusively through the phone number printed on the back of your physical card or official banking app.",
        "immediate_steps": [
            {
                "order": 1,
                "action": "Block / Freeze the Compromised Card Immediately",
                "priority": "CRITICAL",
                "instructions": "Open your official mobile banking app and instantly freeze/block international and domestic transactions on the exposed card."
            },
            {
                "order": 2,
                "action": "Contact Bank Fraud Helpline",
                "priority": "CRITICAL",
                "instructions": "Call your bank's dedicated 24/7 card fraud helpline to request permanent card cancellation and hotlisting."
            },
            {
                "order": 3,
                "action": "Review Recent Statements for Unauthorized Debits",
                "priority": "HIGH",
                "instructions": "Audit recent mini-statements for micro-debits (often used by scammers to test card validity) and dispute unauthorized charges within 24 hours."
            }
        ]
    },
    "shared_otp": {
        "headline": "Authentication Token (OTP) Breach Protocol",
        "severity": "CRITICAL",
        "caution_note": "An OTP is a one-time cryptographic authorization. If shared, a transaction or account takeover may be executing in real-time.",
        "immediate_steps": [
            {
                "order": 1,
                "action": "Call Your Bank's Emergency Fraud Hotline",
                "priority": "CRITICAL",
                "instructions": "Call your bank immediately to freeze your account/net banking portal. Explain that an OTP was accidentally exposed to an unauthorized third party."
            },
            {
                "order": 2,
                "action": "Change Account Login & Transaction Passwords",
                "priority": "CRITICAL",
                "instructions": "If the OTP was related to email, social media, or cloud accounts, immediately reset passwords via a trusted device."
            },
            {
                "order": 3,
                "action": "Check Linked Mobile Number & Recovery Email",
                "priority": "HIGH",
                "instructions": "Verify that the attacker did not add unauthorized recovery email addresses or phone numbers to your account."
            }
        ]
    },
    "shared_upi_pin": {
        "headline": "UPI PIN Exposure Emergency Containment",
        "severity": "CRITICAL",
        "caution_note": "A UPI PIN is ONLY used to DEBIT funds from your account. Receiving money NEVER requires entering your UPI PIN.",
        "immediate_steps": [
            {
                "order": 1,
                "action": "Reset UPI PIN Immediately in Your UPI App",
                "priority": "CRITICAL",
                "instructions": "Open Google Pay, PhonePe, Paytm, or BHIM. Go to Bank Account settings -> 'Change UPI PIN' immediately using your debit card details."
            },
            {
                "order": 2,
                "action": "Temporary Account Debit Freeze",
                "priority": "CRITICAL",
                "instructions": "If you suspect unauthorized transfers have begun, contact your bank or use netbanking to temporarily disable UPI transactions."
            },
            {
                "order": 3,
                "action": "Audit Active UPI Mandates & Autopay",
                "priority": "HIGH",
                "instructions": "Check your UPI app for any newly created recurring autopay mandates or scheduled debits and cancel them immediately."
            }
        ]
    },
    "sent_money": {
        "headline": "Fraudulent Fund Transfer Incident Response",
        "severity": "CRITICAL",
        "caution_note": "Time is of the essence. Reporting within the golden hour (first 2-4 hours) dramatically increases the probability of funds being frozen in the beneficiary account.",
        "immediate_steps": [
            {
                "order": 1,
                "action": "Report to National Cyber Crime Portal (Helpline 1930 / cybercrime.gov.in)",
                "priority": "CRITICAL",
                "instructions": "In India, immediately dial 1930 (Citizen Financial Cyber Fraud Reporting Management System) to file an emergency freeze alert on the transaction."
            },
            {
                "order": 2,
                "action": "File Dispute / Chargeback with Your Bank & UPI Provider",
                "priority": "CRITICAL",
                "instructions": "Submit the UPI UTR number or bank transaction reference ID to your bank's fraud department and request an immediate recall of funds."
            },
            {
                "order": 3,
                "action": "Preserve Evidence Forensically",
                "priority": "HIGH",
                "instructions": "Do not delete WhatsApp chats, Telegram threads, emails, payment screenshots, or SMS transaction messages. Export them securely."
            }
        ]
    },
    "downloaded_file": {
        "headline": "Untrusted File / Malware Containment Protocol",
        "severity": "HIGH",
        "caution_note": "Do not open, execute, or install the downloaded file (especially .apk, .exe, .scr, or .zip files).",
        "immediate_steps": [
            {
                "order": 1,
                "action": "Disconnect Device from Wi-Fi & Mobile Data",
                "priority": "CRITICAL",
                "instructions": "Turn on Airplane Mode or disconnect from the internet immediately to prevent potential malware from establishing command-and-control communication."
            },
            {
                "order": 2,
                "action": "Delete the File from Downloads & Empty Trash",
                "priority": "HIGH",
                "instructions": "Permanently delete the downloaded file without opening or launching it."
            },
            {
                "order": 3,
                "action": "Perform a Full Security Scan",
                "priority": "HIGH",
                "instructions": "Scan your system using a trusted endpoint antivirus or security software (e.g. Windows Defender, Malwarebytes)."
            }
        ]
    },
    "shared_aadhaar_pan": {
        "headline": "Identity Document Exposure Mitigation",
        "severity": "HIGH",
        "caution_note": "Aadhaar and PAN details can be misused for unauthorized SIM card issuance, loan applications, or shell business registrations.",
        "immediate_steps": [
            {
                "order": 1,
                "action": "Lock Your Biometrics in mAadhaar / UIDAI Portal",
                "priority": "CRITICAL",
                "instructions": "Log into the official UIDAI myAadhaar portal (myaadhaar.uidai.gov.in) and turn on 'Lock Biometrics' to prevent biometric authentication misuse."
            },
            {
                "order": 2,
                "action": "Check SIM Cards Registered Under Your Name",
                "priority": "HIGH",
                "instructions": "Visit the Department of Telecommunications TAFCOP portal (tafcop.sancharsaathi.gov.in) to verify all mobile numbers issued under your identity."
            },
            {
                "order": 3,
                "action": "Monitor Credit Bureau Reports (CIBIL / Experian)",
                "priority": "HIGH",
                "instructions": "Check your credit report regularly to ensure no unauthorized loan applications or credit cards have been opened using your PAN."
            }
        ]
    },
    "opened_website": {
        "headline": "Suspicious Website Visit Protocol",
        "severity": "MODERATE",
        "caution_note": "If you only visited the page without typing passwords, downloading files, or submitting forms, your risk is typically minimal.",
        "immediate_steps": [
            {
                "order": 1,
                "action": "Close the Browser Tab & Clear Recent Cache/Cookies",
                "priority": "HIGH",
                "instructions": "Close the suspicious tab. In browser settings, clear recent cookies and cache for that specific site to remove tracking tokens."
            },
            {
                "order": 2,
                "action": "Verify No Automatic Downloads Were Initiated",
                "priority": "HIGH",
                "instructions": "Check your browser download history to ensure no stealth drive-by downloads occurred."
            },
            {
                "order": 3,
                "action": "Keep Browser Updated",
                "priority": "RECOMMENDED",
                "instructions": "Ensure your browser is on the latest version with current security patches."
            }
        ]
    }
}

NATIONAL_HELPLINES = {
    "India National Cyber Crime Helpline": "1930",
    "India Cyber Crime Reporting Portal": "cybercrime.gov.in",
    "India TAFCOP (Check SIMs in your name)": "tafcop.sancharsaathi.gov.in",
    "UIDAI Aadhaar Lock Support": "1947",
    "US IC3 (Internet Crime Complaint Center)": "ic3.gov",
    "UK Action Fraud": "0300 123 2040"
}

def get_emergency_guidance(incident_type: str) -> Dict[str, Any]:
    """Retrieves step-by-step crisis containment instructions for victim triage"""
    normalized = incident_type.lower().strip()
    alias_map = {
        "money_sent": "sent_money",
        "i_sent_money": "sent_money",
        "sent_money": "sent_money",
        "password_entered": "entered_password",
        "i_entered_my_password": "entered_password",
        "entered_password": "entered_password",
        "card_entered": "entered_card",
        "i_entered_card_details": "entered_card",
        "entered_card": "entered_card",
        "otp_shared": "shared_otp",
        "i_shared_otp": "shared_otp",
        "shared_otp": "shared_otp",
        "upi_pin_shared": "shared_upi_pin",
        "i_shared_upi_pin": "shared_upi_pin",
        "shared_upi_pin": "shared_upi_pin",
        "file_downloaded": "downloaded_file",
        "i_downloaded_a_file": "downloaded_file",
        "downloaded_file": "downloaded_file",
        "aadhaar_pan_shared": "shared_aadhaar_pan",
        "i_shared_aadhaar_pan": "shared_aadhaar_pan",
        "shared_aadhaar_pan": "shared_aadhaar_pan",
        "website_opened": "opened_website",
        "i_only_opened_the_website": "opened_website",
        "opened_website": "opened_website"
    }
    key = alias_map.get(normalized, normalized)
    guidance = EMERGENCY_INCIDENT_GUIDANCE.get(key, EMERGENCY_INCIDENT_GUIDANCE["opened_website"])
    return {
        "incident_type": incident_type,
        "headline": guidance["headline"],
        "severity": guidance["severity"],
        "caution_note": guidance["caution_note"],
        "immediate_steps": guidance["immediate_steps"],
        "helpline_numbers": NATIONAL_HELPLINES
    }
