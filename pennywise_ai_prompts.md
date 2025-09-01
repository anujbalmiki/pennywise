# AI Build Prompts for SMS Parsing Project - Pennywise

This document contains detailed AI prompts to build each major component of your SMS parsing and analytics system separately: React Native Android app, Next.js web frontend, and FastAPI backend.

---

## React Native Android App (SMS Listener) - Pennywise

Build a React Native Android app with the following detailed specifications:

- Implement **Firebase Authentication** for user login, supporting OTP-based phone authentication and email/password login.
- After successful login, obtain and securely store the Firebase ID token for authenticating backend requests.
- Implement a **background service or SMS listener module** that captures incoming SMS messages silently and in real-time.
- Extract complete SMS text and metadata (timestamp, sender number) from every received message.
- Send the SMS data along with Firebase ID token securely to a FastAPI backend API endpoint.
- Ensure background SMS listening continues even when the app is closed or in the background, respecting Android 8+ background execution limits.
- Properly handle all required Android permissions for SMS reading and background execution with clear user prompts.
- Provide a minimal UI:
  - Login screen with Firebase Authentication.
  - Home screen that indicates SMS listener status.
  - Logout button to clear user session locally.
- Maintain independent session management such that logging out from the mobile app or web frontend does not affect the other.
- Support Android API level 26 and above.
- Use modern React Native conventions, functional components, and hooks.
- Provide inline comments and a README detailing setup steps, Firebase configuration, permissions, and running the app.

---

## Next.js Web Frontend (User Dashboard) - Pennywise


Build a Next.js web frontend based on these detailed requirements:

- Use **Firebase Authentication** for user login/logout supporting OTP, email/password, and social login.
- After login, acquire the Firebase ID token and use it to authorize API requests to the FastAPI backend.
- Dashboard must include:
  - Weekly and monthly spending summaries with clear visualization.
  - Interactive charts (cash flow, category spend, merchant breakdown, trends over time).
  - Powerful search and filter interfaces for transactions (date ranges, merchants, categories, payment modes, remarks).
  - Import capability for CSV, XML, and TXT bank statements with backend processing.
  - Export options for reports in PDF and Excel formats.
- Support transaction management UI:
  - View detailed transactions.
  - Edit categories and merchant tags.
  - Add remarks/notes.
  - Display flagged failed transactions visually distinct.
- Implement user profile controls for login/logout and security settings; user sessions are independent of mobile app sessions.
- Design a clean, mobile-friendly, minimalistic UI.
- Use React functional components with hooks and state management (e.g., Redux or Context API).
- Utilize charting libraries compatible with React such as Recharts or Victory.
- Include a README for setup, Firebase integration, running and deployment instructions.

---

## FastAPI Backend (SMS API & Processing) - Pennywise

Build a FastAPI backend fulfilling these comprehensive requirements:

- Integrate the **Firebase Admin SDK** to verify Firebase ID tokens on every protected endpoint to authenticate users.
- Implement REST endpoints to:
  - Receive SMS data (full text, timestamp, sender) from the mobile React Native app with authentication.
  - Accept backup files (CSV, XML, TXT), parse transactions using Gemini API or equivalent logic.
  - Export transaction data and reports as PDFs, Excels, or SQL dumps.
  - Search/filter transactions using multiple parameters (date, amount, category, merchant, tags, remarks).
  - Provide analytics endpoints for summaries, recurring payment detection, tagging merchants/categories, and flagging failed transactions.
- Store all user data, SMS messages, and transactions securely in **MongoDB**, keyed by Firebase user UID.
- Validate and sanitize all user inputs.
- Authenticate each request via Firebase token verification.
- Provide detailed error handling and logging.
- Modularize code into clear services:
  - SMS parsing
  - Backup file parsing
  - Analytics and reporting
  - User management
- Offer automatic OpenAPI/Swagger documentation with usage examples.
- Include unit and integration tests covering main features.
- Supply a comprehensive README with:
  - Firebase project and Firebase Admin SDK setup guide.
  - MongoDB Atlas or local setup instructions and connection details.
  - Run and deploy instructions.
  - Guidelines for managing secrets and environment variables securely.

---

# Summary

This document provides fully detailed, no-assumption AI prompts to build the SMS Listener React Native app, Next.js dashboard, and FastAPI backend components independently while ensuring the whole system integrates securely and efficiently around Firebase Authentication and MongoDB data storage.

Each component prompt includes explicit functional and non-functional requirements, expected user flows, integration details, security considerations, and developer guidance for setup and deployment.

Use these prompts to clearly direct AI or developer teams for comprehensive feature-complete app component development.