# ASD Tier 2 Installer Repository

## Overview
A professional, lightweight web application that connects to the GitHub repository `https://github.com/ASD-T2/ASD_Installer-repo` to list available installer files for authorized team members to download.

## Project Architecture

### Backend (Flask)
- **app.py**: Main Flask application with authentication and GitHub API integration
- Session-based authentication using Flask sessions
- GitHub API integration to fetch installer files dynamically
- Credentials stored in Replit Secrets

### Frontend
- **templates/login.html**: Login page with username/password authentication
- **templates/dashboard.html**: Main dashboard displaying installer files
- Tailwind CSS for responsive, professional design
- Real-time search and filter functionality

### GitHub Integration
- Uses authorized GitHub connection: `conn_github_01K8RPX7KYMMSGRB3VP5W2V7MJ`
- Fetches files from: `https://github.com/ASD-T2/ASD_Installer-repo`
- Direct download links to GitHub raw files

## Required Secrets
Configure these in Replit Secrets:
- `SESSION_SECRET`: Flask session secret key (already configured)
- `APP_USERNAME`: Login username (defaults to "admin" if not set)
- `APP_PASSWORD`: Login password (defaults to "password" if not set)
- `GITHUB_TOKEN`: GitHub personal access token (optional, for rate limit increase)

## Features Implemented
- ✅ Simple username/password authentication
- ✅ Session-based login system
- ✅ Professional dashboard with installer file cards
- ✅ Dynamic file listing from GitHub API
- ✅ File information display (name, version, description, size)
- ✅ Direct download buttons to GitHub raw files
- ✅ Responsive design with Tailwind CSS
- ✅ Search and filter functionality
- ✅ Logout functionality

## Technical Stack
- Python 3.11
- Flask 3.1.2
- Requests library for GitHub API
- Tailwind CSS (CDN)
- Session management with Flask sessions

## Project Structure
```
.
├── app.py                 # Main Flask application
├── templates/
│   ├── login.html        # Login page
│   └── dashboard.html    # Installer dashboard
├── .gitignore            # Git ignore file
├── pyproject.toml        # Python dependencies
└── replit.md             # Project documentation
```

## Recent Changes
- **2025-10-29**: Initial project setup
  - Created Flask application with authentication
  - Integrated GitHub API for file listing
  - Built responsive dashboard with Tailwind CSS
  - Implemented search and filter functionality
  - Configured for Replit free tier hosting

## User Preferences
- Language: English
- Design: Professional, clean, responsive
- Deployment: Replit free tier (no Always-On)

## Notes
- Application runs on port 5000
- No database required - read-only GitHub access
- Lightweight and optimized for free tier limits
- All installer files hosted on GitHub, not on Replit
