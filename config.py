"""
NER-LogiX System Configuration & Credential Store
"""
import os

API_KEY = os.environ.get("NER_API_KEY", os.environ.get("CODEBUFF_API_KEY", "cb1_3z07_1_c7585b52b7d49dc081b2f48d"))
IS_AUTHENTICATED = bool(API_KEY)
MASKED_API_KEY = f"{API_KEY[:4]}...{API_KEY[-4:]}" if len(API_KEY) > 8 else "***"
PORT = int(os.environ.get("PORT", 8080))
