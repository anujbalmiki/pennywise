# test_token_generator.py
import firebase_admin
from firebase_admin import auth, credentials

# Initialize Firebase Admin SDK
cred = credentials.Certificate("E:\Downloads\pennywise-ab-firebase-adminsdk-fbsvc-49573bced7.json")
firebase_admin.initialize_app(cred)

# Create a custom token for testing
custom_token = auth.create_custom_token("test_user_123")

print(f"Custom Token: {custom_token}")