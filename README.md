# Pennywise Backend

A FastAPI backend for SMS-based transaction tracking and analytics powered by **Google Gemini AI**. This application intelligently parses SMS messages from banks and credit cards using AI to extract transaction information and provides comprehensive financial analytics.

## 🚀 Key Features

- **🤖 AI-Powered SMS Parsing**: Uses Google Gemini AI to intelligently parse any SMS format from banks and credit cards
- **🧠 Intelligent SMS Filtering**: AI determines if an SMS contains transaction information before processing
- **📁 Backup File Processing**: Supports CSV, XML, TXT, JSON, and PDF files with AI-powered parsing
- **💳 Transaction Management**: Store, categorize, and manage financial transactions
- **📊 Analytics**: Comprehensive spending analytics and insights
- **🔐 Firebase Authentication**: Secure user authentication using Firebase
- **🗄️ MongoDB Storage**: Scalable NoSQL database for data storage
- **🔄 Auto-categorization**: Intelligent transaction categorization based on merchant names
- **📈 Recurring Transaction Detection**: Identify patterns in recurring payments
- **📤 Export Capabilities**: Export transaction data in multiple formats

## 🏦 Universal Bank Support

Unlike traditional regex-based parsers, **Gemini AI can parse SMS from ANY bank or credit card** by understanding the context and extracting transaction details intelligently. This includes:

- **Federal Bank** (AX-FEDBNK-S)
- **SBI Card** (VM-SBICRD-S) 
- **SBI UPI** (VM-SBIUPI-S)
- **Axis Bank** (AX-AXISBK-S)
- **OneCard** (CP-OneCrd-S)
- **Any other bank** - Gemini AI adapts to new formats automatically!

## 📁 Backup File Support

Upload and process backup files from banks and credit card statements:

- **CSV Files**: Bank statements, credit card statements
- **XML Files**: Structured financial data
- **PDF Files**: Statement PDFs (text extraction)
- **TXT Files**: Plain text statements
- **JSON Files**: Structured transaction data

## Prerequisites

- Python 3.8+
- MongoDB (local or Atlas)
- Firebase project with Admin SDK
- **Google Gemini API key** (for AI-powered parsing)

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd pennywise-backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp env.example .env
   # Edit .env with your configuration
   ```

5. **Configure Firebase**
   - Go to your Firebase project console
   - Navigate to Project Settings > Service Accounts
   - Generate a new private key
   - Download the JSON file and extract the values to your `.env` file

6. **Get Gemini API Key**
   - Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a new API key
   - Add it to your `.env` file as `GEMINI_API_KEY`

7. **Set up MongoDB**
   - Install MongoDB locally or use MongoDB Atlas
   - Update the `MONGODB_URI` in your `.env` file

## Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Firebase Configuration
FIREBASE_PROJECT_ID=your-firebase-project-id
FIREBASE_PRIVATE_KEY_ID=your-private-key-id
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nYour private key here\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL=firebase-adminsdk-xxxxx@your-project.iam.gserviceaccount.com
FIREBASE_CLIENT_ID=your-client-id
FIREBASE_CLIENT_X509_CERT_URL=https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-xxxxx%40your-project.iam.gserviceaccount.com

# MongoDB Configuration
MONGODB_URI=mongodb://localhost:27017
MONGODB_DATABASE=pennywise

# Gemini AI Configuration (Required for AI parsing)
GEMINI_API_KEY=your-gemini-api-key

# Application Configuration
APP_NAME=Pennywise Backend
APP_VERSION=1.0.0
DEBUG=false

# Security
SECRET_KEY=your-secret-key-here-change-this-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

## Running the Application

### Development Mode
```bash
python start.py
# or
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

The application will be available at:
- API: http://localhost:8000
- Documentation: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Endpoints

### Authentication
All endpoints require Firebase authentication. Include the Firebase ID token in the Authorization header:
```
Authorization: Bearer <firebase-id-token>
```

### SMS Endpoints
- `POST /api/v1/sms/` - Receive SMS from mobile app (AI-powered parsing with intelligent filtering)
- `GET /api/v1/sms/` - Get SMS messages
- `GET /api/v1/sms/{sms_id}` - Get specific SMS
- `POST /api/v1/sms/reprocess` - Reprocess unparsed SMS with AI
- `GET /api/v1/sms/statistics/summary` - Get SMS statistics
- `DELETE /api/v1/sms/{sms_id}` - Delete SMS message

### Backup File Endpoints
- `POST /api/v1/backup/upload` - Upload and process backup files (CSV, XML, PDF, etc.)
- `POST /api/v1/backup/validate` - Validate backup file before processing
- `GET /api/v1/backup/stats` - Get backup processing statistics

### Transaction Endpoints
- `POST /api/v1/transactions/` - Create transaction manually
- `GET /api/v1/transactions/` - Get transactions with filters
- `GET /api/v1/transactions/{transaction_id}` - Get specific transaction
- `PUT /api/v1/transactions/{transaction_id}` - Update transaction
- `DELETE /api/v1/transactions/{transaction_id}` - Delete transaction
- `GET /api/v1/transactions/analytics/summary` - Get analytics
- `GET /api/v1/transactions/recurring/detect` - Detect recurring transactions
- `GET /api/v1/transactions/export/{format}` - Export transactions

### User Endpoints
- `GET /api/v1/users/me` - Get current user info
- `PUT /api/v1/users/me` - Update user info
- `DELETE /api/v1/users/me` - Delete user account
- `GET /api/v1/users/stats` - Get user statistics

## 🤖 AI-Powered SMS Processing

### How It Works

The mobile app sends **ALL SMS messages** to the backend, and the AI intelligently determines which ones contain transaction information in a **single, efficient API call**:

1. **SMS Reception**: Mobile app sends ALL SMS to `/api/v1/sms/`
2. **Single AI Analysis**: Gemini AI analyzes the SMS and determines if it's transactional
3. **Intelligent Processing**: 
   - If transactional → extracts all transaction details
   - If non-transactional → skips processing
4. **Database Storage**: Transaction saved with confidence scores and reasoning

### Intelligent SMS Filtering

The AI can distinguish between:

**✅ Transactional SMS (Processed):**
- "Rs 500 spent on card at Amazon"
- "INR 1000 credited to your account"
- "UPI payment of Rs 250 to merchant"
- "Card transaction of Rs 1500 at restaurant"

**❌ Non-Transactional SMS (Skipped):**
- "Your OTP is 123456"
- "Welcome to our banking service"
- "Your account statement is ready"
- "Please update your KYC details"
- "Happy birthday! Special offers for you"

### Example SMS Processing Flow

```
📱 Mobile App sends ALL SMS:
├── "Rs 500 spent on card" → ✅ Transaction detected → Parsed and saved
├── "Your OTP is 123456" → ❌ Not transactional → Skipped
├── "Welcome to our service" → ❌ Not transactional → Skipped
└── "INR 1000 credited" → ✅ Transaction detected → Parsed and saved
```

### AI Detection Features

- **Single API Call**: Efficient single request to Gemini AI for both detection and parsing
- **Context Understanding**: Analyzes SMS content intelligently
- **Confidence Scoring**: Provides confidence level for each detection
- **Reason Explanation**: Explains why SMS was classified as transactional or not
- **Flexible Detection**: Works with any SMS format or language
- **Fallback Support**: Uses pattern matching when AI is unavailable

### Example SMS Formats (AI handles all variations)

**Federal Bank UPI:**
```
Rs 10.00 sent via UPI on 25-08-2025 17:42:18 to IRCTC UTS Ref No. 560316544643
```

**SBI Card (any variation):**
```
Rs.548.00 spent on your SBI Credit Card ending with 2985 at Airtel on 24-08-25 via UPI (Ref No. 560205419474)
```

**Axis Bank (any format):**
```
Spent Card no. XX7613 INR 506.22 21-08-25 23:10:52 Hostinger P Avl Lmt INR 20614.3
```

**Any New Bank**: Gemini AI adapts to new SMS formats automatically!

### AI Extracts:
- Transaction amount
- Transaction type (credit/debit/payment)
- Merchant name
- Transaction date and time
- Reference number
- Account/card number (masked)
- Payment method (UPI/Card/NEFT/etc.)
- Bank name detection
- **Detection confidence score**
- **Classification reason**

## 📁 Backup File Processing

### Supported Formats

**CSV Files:**
```csv
Date,Amount,Description,Type
2025-01-15,500.00,Amazon Purchase,Debit
2025-01-16,1000.00,Salary Credit,Credit
```

**XML Files:**
```xml
<transactions>
  <transaction>
    <date>2025-01-15</date>
    <amount>500.00</amount>
    <description>Amazon Purchase</description>
    <type>Debit</type>
  </transaction>
</transactions>
```

**PDF Files**: Text extraction from statement PDFs
**TXT Files**: Plain text statements
**JSON Files**: Structured transaction data

### Processing Flow

1. **File Upload**: Send file to `/api/v1/backup/upload`
2. **AI Analysis**: Gemini AI analyzes file content and extracts transactions
3. **Batch Processing**: Multiple transactions processed in one request
4. **Database Storage**: All transactions saved to MongoDB

## Database Schema

### Collections

1. **users** - User information
2. **sms_messages** - Raw SMS messages (all SMS, including non-transactional)
3. **transactions** - Parsed transactions (from SMS and backup files)
4. **categories** - Transaction categories
5. **merchants** - Merchant information

### Indexes

The application automatically creates indexes for optimal performance:
- User-based queries
- Date-based sorting
- Text search on merchant names
- Transaction type filtering

## Development

### Project Structure
```
app/
├── __init__.py
├── main.py              # FastAPI application
├── config.py            # Configuration settings
├── database.py          # Database connection
├── models.py            # Pydantic models
├── auth.py              # Firebase authentication
├── routers/             # API routes
│   ├── __init__.py
│   ├── sms.py
│   ├── transactions.py
│   ├── users.py
│   └── backup.py        # Backup file processing
└── services/            # Business logic
    ├── __init__.py
    ├── sms_parser.py    # AI-powered SMS parsing with intelligent filtering
    ├── sms_service.py   # SMS management
    ├── transaction_service.py
    └── backup_service.py # Backup file processing
```

### AI Parsing Benefits

**Traditional Regex Approach:**
- ❌ Rigid patterns
- ❌ Breaks with format changes
- ❌ Limited to known banks
- ❌ High maintenance
- ❌ No intelligent filtering

**Gemini AI Approach:**
- ✅ Flexible and adaptive
- ✅ Handles any SMS format
- ✅ Works with new banks automatically
- ✅ Low maintenance
- ✅ Intelligent context understanding
- ✅ **Smart filtering of non-transactional SMS**
- ✅ **Single API call for detection + parsing**

### Testing

Run tests with pytest:
```bash
pytest
```

## Deployment

### Docker

Create a `Dockerfile`:
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Environment Variables for Production

- Set `DEBUG=false`
- Use strong `SECRET_KEY`
- Configure proper CORS origins
- Use MongoDB Atlas or production MongoDB instance
- Set up proper Firebase project
- **Ensure Gemini API key is configured**

## Security Considerations

- All endpoints require Firebase authentication
- Input validation using Pydantic models
- SQL injection protection (MongoDB)
- CORS configuration
- Environment variable management
- Request logging and monitoring
- **Gemini API key security**

## Performance

### AI Parsing Performance
- **SMS Processing**: ~1-2 seconds per SMS (single API call)
- **Backup Files**: ~5-10 seconds for typical files
- **Batch Processing**: Efficient handling of multiple transactions
- **Fallback Support**: Regex parsing when AI is unavailable
- **Resource Optimization**: Single Gemini API call eliminates duplicate requests

### Scalability
- Asynchronous processing
- Database indexing for fast queries
- Connection pooling
- Efficient memory usage
- **Intelligent filtering reduces processing load**
- **Optimized API usage reduces costs and latency**

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support and questions:
- Create an issue in the repository
- Check the API documentation at `/docs`
- Review the logs for debugging information

## 🤖 AI-Powered Features Summary

- **Universal SMS Parsing**: Works with any bank or credit card
- **Intelligent SMS Filtering**: Automatically detects and skips non-transactional SMS
- **Context Understanding**: Extracts transaction details accurately
- **Backup File Processing**: Handles CSV, XML, PDF, TXT, JSON files
- **Adaptive Learning**: Improves parsing with different formats
- **Fallback Support**: Regex parsing when AI is unavailable
- **Batch Processing**: Efficient handling of multiple transactions
- **Confidence Scoring**: Provides confidence levels for AI decisions
- **Resource Optimization**: Single API call for maximum efficiency
