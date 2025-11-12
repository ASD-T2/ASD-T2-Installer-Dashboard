import os
import sys
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import requests
import time

# Simple in-memory cache
CACHE = {
    "timestamp": 0,
    "data": []
}

CACHE_TTL = 300  # seconds (5 minutes)

required_secrets = ['SESSION_SECRET', 'APP_USERNAME', 'APP_PASSWORD']
missing_secrets = [secret for secret in required_secrets if not os.environ.get(secret)]

if missing_secrets:
    print(f"ERROR: Required secrets are not configured: {', '.join(missing_secrets)}", file=sys.stderr)
    print("Please set these environment variables in Replit Secrets before running the application.", file=sys.stderr)
    sys.exit(1)

app = Flask(__name__)
app.secret_key = os.environ.get('SESSION_SECRET')

GITHUB_REPO_OWNER = 'ASD-T2'
GITHUB_REPO_NAME = 'ASD_Installer-repo'
GITHUB_API_URL = "https://api.github.com/repos/ASD-T2/ASD_Installer-repo/contents/installers"


def get_github_token():
    return os.environ.get('GITHUB_TOKEN', '')

def check_credentials(username, password):
    valid_username = os.environ.get('APP_USERNAME')
    valid_password = os.environ.get('APP_PASSWORD')
    return username == valid_username and password == valid_password

def fetch_installer_files():
    try:
        # Check cache first
        now = time.time()
        if CACHE["data"] and (now - CACHE["timestamp"] < CACHE_TTL):
            print("[DEBUG] Using cached installer list")
            return CACHE["data"], None

        # No valid cache — fetch from GitHub
        headers = {}
        github_token = get_github_token()
        if github_token:
            headers['Authorization'] = f'token {github_token}'
        print(f"[DEBUG] GitHub token loaded: {'Yes' if github_token else 'No'}")

        installer_files = []
        fetch_files_recursive(GITHUB_API_URL, headers, installer_files)

        # Update cache
        CACHE["data"] = installer_files
        CACHE["timestamp"] = time.time()
        print("[DEBUG] Cache updated with new data")

        return installer_files, None

    except requests.exceptions.RequestException as e:
        error_msg = f"Failed to connect to GitHub: {str(e)}"
        print(f"Error fetching files: {error_msg}")
        return [], error_msg
    except Exception as e:
        error_msg = f"An unexpected error occurred: {str(e)}"
        print(f"Error fetching files: {error_msg}")
        return [], error_msg

def fetch_files_recursive(url, headers, installer_files, path=''):
    try:
        response = requests.get(url, headers=headers, timeout=10)
        print(f"[DEBUG] Fetching from: {url}")
        print(f"[DEBUG] API Status: {response.status_code}")
        if response.status_code != 200:
            print(f"[DEBUG] Response snippet: {response.text[:200]}")

        if response.status_code == 200:
            items = response.json()
            
            for item in items:
                if item['type'] == 'file':
                    file_name = item['name']
                    file_size = item.get('size', 0)
                    download_url = item['download_url']
                    file_path = f"{path}/{file_name}" if path else file_name
                    
                    version = extract_version(file_name)
                    description = generate_description(file_name)
                    
                    installer_files.append({
                        'name': file_name,
                        'path': file_path,
                        'version': version,
                        'description': description,
                        'size': format_file_size(file_size),
                        'download_url': download_url
                    })
                elif item['type'] == 'dir':
                    new_path = f"{path}/{item['name']}" if path else item['name']
                    fetch_files_recursive(item['url'], headers, installer_files, new_path)
        elif response.status_code == 404:
            print(f"Repository or path not found: {url}")
        elif response.status_code == 403:
            print(f"Access forbidden (rate limit or permissions): {url}")
        else:
            print(f"GitHub API returned status {response.status_code} for {url}")
    except Exception as e:
        print(f"Error fetching {url}: {e}")

def extract_version(filename):
    import re
    version_pattern = r'v?(\d+\.?\d*\.?\d*\.?\d*)'
    match = re.search(version_pattern, filename)
    if match:
        return match.group(1)
    return 'N/A'

def generate_description(filename):
    name_lower = filename.lower()
    if 'setup' in name_lower or 'installer' in name_lower:
        return 'Installation package'
    elif 'update' in name_lower or 'patch' in name_lower:
        return 'Update/Patch file'
    elif '.exe' in name_lower:
        return 'Windows executable'
    elif '.msi' in name_lower:
        return 'Windows installer package'
    elif '.zip' in name_lower or '.tar' in name_lower or '.gz' in name_lower:
        return 'Compressed archive'
    else:
        return 'Installer file'

def format_file_size(size_bytes):
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"

@app.route('/')
def index():
    if 'logged_in' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '')
        password = request.form.get('password', '')
        
        if check_credentials(username, password):
            session['logged_in'] = True
            session['username'] = username
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error='Invalid credentials')
    
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'logged_in' not in session:
        return redirect(url_for('login'))
    
    installer_files, error = fetch_installer_files()
    return render_template('dashboard.html', files=installer_files, error=error, username=session.get('username'))

@app.route('/api/files')
def api_files():
    if 'logged_in' not in session:
        return jsonify({'error': 'Unauthorized'}), 401
    
    installer_files, error = fetch_installer_files()
    if error:
        return jsonify({'error': error, 'files': []}), 500
    return jsonify(installer_files)
from flask import send_file
import io

@app.route('/download/<path:file_path>')
def download_file(file_path):
    # Ensure user is logged in
    if 'logged_in' not in session:
        return redirect(url_for('login'))

    # Construct the GitHub API URL for the file
    api_url = f"https://api.github.com/repos/{GITHUB_REPO_OWNER}/{GITHUB_REPO_NAME}/contents/installers/{file_path}"

    headers = {}
    github_token = get_github_token()
    if github_token:
        headers['Authorization'] = f'token {github_token}'

    # Get metadata for the file
    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        content = response.json()
        download_url = content.get('download_url')
        if not download_url:
            return "Download URL not found in response.", 400

        # Fetch the actual file data
        file_data = requests.get(download_url).content
        filename = file_path.split('/')[-1]

        return send_file(
            io.BytesIO(file_data),
            as_attachment=True,
            download_name=filename
        )
    elif response.status_code == 404:
        return f"File not found: {file_path}", 404
    elif response.status_code == 403:
        return "Access forbidden — check your GitHub token permissions.", 403
    else:
        return f"Unexpected error ({response.status_code}) retrieving file.", 500

@app.route('/clear_cache', methods=['POST'])
def clear_cache():
    if 'logged_in' not in session:
        return jsonify({"status": "error", "message": "Unauthorized"}), 401

    CACHE["data"] = []
    CACHE["timestamp"] = 0
    print("[DEBUG] Cache cleared manually via Refresh button")
    return jsonify({"status": "success", "message": "Cache cleared"})

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

from flask import request  # if not already at the top of your file

@app.route('/ping')
def ping():
    # Retrieve key from URL parameter (?key=YOURSECRET)
    provided_key = request.args.get('key')

    # Compare it with your stored secret
    expected_key = os.environ.get('PING_KEY')

    if provided_key != expected_key:
        return 'unauthorized', 403

    return 'pong', 200

@app.before_first_request
def warm_up():
    print("[INFO] App warmed up and ready.")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)
