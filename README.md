# Nomisma - Coin Analysis & Cataloging System

![CI/CD](https://github.com/nikolareljin/nomisma/workflows/CI%2FCD%20Pipeline/badge.svg)

🪙 A comprehensive coin analysis and cataloging application with AI-powered identification, valuation, and eBay integration.

   Named after the [Greek word for "money"](#nomisma), Nomisma honors the history of coinage at the heart of this project. 

<img width="861" height="551" alt="image" src="https://github.com/user-attachments/assets/25904dff-ad6a-4f00-9469-e4f344f6978c" />


## Features

- 🔬 **Digital Microscope Integration** - Capture high-resolution coin images using USB microscopes (DM7-Z01C or compatible)
- 🤖 **AI-Powered Analysis** - Automatic coin identification, grading, and defect detection using Google Gemini Vision
- 💰 **Value Estimation** - AI-driven market value estimates based on condition and rarity
- 📊 **Comprehensive Cataloging** - Track coins with detailed metadata, images, and analysis history
- 🔍 **Advanced Search** - Search by inventory number, country, year, denomination, and more
- 🛒 **eBay Integration** - One-click listing creation with pre-populated data
- 📦 **Docker Deployment** - Fully containerized for easy setup and deployment

## Quick Start

### Prerequisites

- Docker and Docker Compose installed
- USB digital microscope (optional, for scanning)
- Google Gemini API key (for AI analysis)
- eBay Developer credentials (optional, for marketplace integration)

### Installation

1. **Clone the repository**
   ```bash
   cd /home/nikos/Projects/nomisma
   ```

2. **Initialize git submodules**
   ```bash
   git submodule update --init --recursive
   # Or simply run:
   ./update
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your API keys
   nano .env
   ```

4. **Start the application**
   ```bash
   ./start
   ```

   **Options:**
   - `./start` - Start the application
   - `./start -b` - Rebuild Docker images and start
   - `./start -h` - Show help message

5. **Stop the application**
   ```bash
   ./stop
   ```

   **Options:**
   - `./stop` - Stop containers (data preserved)
   - `./stop -v` - Stop and remove volumes (deletes all data)
   - `./stop -h` - Show help message

The application will be available at:
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

### First-Time Setup

1. **Get a Gemini API Key** (for AI analysis)
   - Visit https://makersuite.google.com/app/apikey
   - Create a new API key
   - Add it to your `.env` file as `GEMINI_API_KEY`

2. **eBay Developer Setup** (optional)
   - Register at https://developer.ebay.com/
   - Create an application to get App ID, Dev ID, and Cert ID
   - Generate a User Token
   - Add credentials to `.env` file

3. **Connect Your Microscope**
   - Plug in your USB microscope
   - The application will auto-detect it on the Scan Coin page
   - See [docs/MICROSCOPE_SETUP.md](docs/MICROSCOPE_SETUP.md) for detailed setup

## Usage

### Scanning a Coin

1. Navigate to **Scan Coin** page
2. Select your microscope from the dropdown
3. Position the coin under the microscope
4. Click **Capture Image**
5. AI will automatically analyze the coin
6. Review and edit the detected information
7. Click **Save Coin**

### Managing Your Collection

- **Dashboard**: View statistics and recent coins
- **Collection**: Browse, search, and filter your coins
- **Coin Details**: View detailed information, AI analysis, and valuations
- **Edit**: Update coin information as needed

### Listing on eBay

1. Open a coin's detail page
2. Click **List on eBay**
3. Review the pre-populated listing information
4. Adjust pricing and description
5. Click **Create Listing**

## Project Structure

```
nomisma/
├── backend/              # Python FastAPI backend
│   ├── app/
│   │   ├── routes/      # API endpoints
│   │   ├── services/    # Business logic
│   │   ├── models.py    # Database models
│   │   └── schemas.py   # Pydantic schemas
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/            # React frontend
│   ├── src/
│   │   ├── pages/      # React pages
│   │   ├── components/ # Reusable components
│   │   └── api.js      # API client
│   ├── Dockerfile
│   └── package.json
├── database/            # PostgreSQL initialization
│   └── init.sql
├── docs/               # Documentation
├── docker-compose.yml  # Container orchestration
└── start              # Startup script
```

## API Documentation

Once the application is running, visit http://localhost:8000/docs for interactive API documentation.

Key endpoints:
- `POST /api/microscope/capture` - Capture image from microscope
- `POST /api/ai/analyze` - Analyze coin image with AI
- `GET /api/coins` - List coins with search/filter
- `POST /api/coins` - Create new coin
- `POST /api/ebay/list` - Create eBay listing

See [docs/API.md](docs/API.md) for complete API reference.

## Development

### Running in Development Mode

**Backend:**
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

### Testing

**All tests (Docker):**
```bash
./test
```

**Single suite (Docker):**
```bash
./test -t backend   # backend pytest
./test -t frontend  # frontend unit tests
./test -t api       # backend /health check
./test -t e2e       # Playwright E2E
```

**Backend (pytest):**
```bash
cd backend
pip install -r requirements.txt
pytest
```

**Frontend unit tests (Vitest):**
```bash
cd frontend
npm install
npm run test
```

**E2E tests (Playwright):**
```bash
cd frontend
npm install
npx playwright install
npm run test:e2e
```

E2E assumes the frontend is running at `http://localhost:3000` and the API at `http://localhost:8000`. Override with `E2E_BASE_URL` or `API_BASE_URL` if needed.

### Database Migrations

The database schema is automatically initialized on first run. To reset:
```bash
docker-compose down -v
docker-compose up -d
```

## Troubleshooting

### Can't Connect to Microscope

- Check USB connection
- Verify camera permissions
- Restart Docker containers
- See [docs/MICROSCOPE_SETUP.md](docs/MICROSCOPE_SETUP.md)

### AI Analysis Fails

- Verify your `GEMINI_API_KEY` is set in `.env`
- Check API quota at https://makersuite.google.com/
- The app will use mock data if no API key is configured

### eBay Listing Fails

- Ensure all eBay credentials are in `.env`
- Verify you're using the correct environment (sandbox vs production)
- Check eBay API status at https://developer.ebay.com/support/api-status

## Utility Scripts

The project includes several utility scripts for managing the application:

### start
Start the Nomisma application
```bash
./start           # Start normally
./start -b        # Rebuild images and start
./start -h        # Show help
```

### stop
Stop the Nomisma application
```bash
./stop            # Stop (preserve data)
./stop -v         # Stop and remove volumes (deletes data!)
./stop -h         # Show help
```

### status
Check application status
```bash
./status          # Show service status
./status -h       # Show help
```

### update
Update git submodules (script-helpers)
```bash
./update          # Update all submodules
./update -h       # Show help
```

**Note:** If script-helpers is not installed, the other scripts will automatically prompt you to run `./update`.

All scripts use the [script-helpers](https://github.com/nikolareljin/script-helpers) library for consistent formatting and error handling.

## CI/CD

The project includes automated GitHub Actions workflows that run on every push and pull request to the main branch:

- **Backend Testing**: Python linting and dependency validation
- **Frontend Testing**: Node.js linting and build verification
- **Docker Build**: Validates all Docker images build successfully
- **Configuration Validation**: Checks required files and docker-compose configuration
- **Security Scanning**: Trivy vulnerability scanner for dependencies

The workflow ensures code quality and prevents broken builds from being merged.

## Documentation

- [API Reference](docs/API.md)
- [Microscope Setup Guide](docs/MICROSCOPE_SETUP.md)
- [eBay Integration Guide](docs/EBAY_INTEGRATION.md)
- [User Guide](docs/USER_GUIDE.md)

## Technology Stack

- **Backend**: Python, FastAPI, SQLAlchemy, PostgreSQL
- **Frontend**: React, Vite, TailwindCSS, React Query
- **AI**: Google Gemini Vision API
- **Image Processing**: OpenCV, Pillow
- **Deployment**: Docker, Docker Compose, Nginx

## License

MIT License - See LICENSE file for details

## Support

For issues and questions:
- Check the [documentation](docs/)
- Review [troubleshooting](#troubleshooting) section
- Open an issue on GitHub

## Inventory System

Each coin is automatically assigned a unique inventory number in the format `NOM-0001`, `NOM-0002`, etc. This short, sequential identifier makes it easy to:
- Label physical storage containers
- Reference coins in conversations
- Maintain organized inventory records
- Track coins across different systems

The inventory number is searchable and displayed prominently throughout the application.

<a name="nomisma">
### Nomisma

Nomisma (νόμισμα) is the Ancient Greek word for money, currency, or a current coin, deriving from nomos (νόμος) meaning "law, custom, or usage," signifying money as something established by convention rather than nature. It specifically referred to official currency, famously the gold Byzantine solidus, and links to the English "numismatics" (study of coins) through Latin.
