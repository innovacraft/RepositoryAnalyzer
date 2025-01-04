from flask import Flask, request, jsonify, send_from_directory
import requests
import os
import logging
import ollama

# Configure logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__, static_folder='../frontend/build', static_url_path='')

@app.route('/')
def index():
    logging.debug(f"Serving index.html from: {os.path.abspath(app.static_folder)}")
    return app.send_static_file('index.html')


@app.route('/files', methods=['GET'])
def fetch_files():
    repo_url = request.args.get('repo_url')
    github_token = request.args.get('github_token')
    branch_name = request.args.get('branch', 'master')  # Default to 'master' if not specified
    logging.debug(f"Fetching files for URL: {repo_url} with token: {github_token} on branch {branch_name}")
    repo_full_name = parse_github_url(repo_url)
    files = fetch_files_from_github(repo_full_name, github_token, branch_name)
    return jsonify(files)


@app.route('/analyze', methods=['POST'])
def analyze_dependencies():
    if not request.is_json:
        logging.error("Request was not in JSON format")
        return jsonify({"error": "Bad request", "message": "The request body must be JSON"}), 400

    logging.debug(f"Received JSON: {request.json}")  # Log the entire request JSON
    content = request.json.get('content')  # Use .get() to avoid KeyError if 'content' key is missing

    if content:
        logging.debug(f"Analyzing content: {content}")
        response = analyze_code(content)
        return jsonify(response)
    else:
        logging.error(f"No content provided. Full JSON Received: {request.json}")
        return jsonify({"error": "No content provided"}), 400




def parse_github_url(url):
    if url.endswith('.git'):
        url = url[:-4]
    parts = url.split('/')
    full_name = '/'.join(parts[-2:])
    logging.debug(f"Parsed GitHub URL to repo full name: {full_name}")
    return full_name

def fetch_files_from_github(repo_full_name, token, branch='master'):
    api_url = f"https://api.github.com/repos/{repo_full_name}/git/trees/{branch}?recursive=1"
    headers = {'Authorization': f'token {token}'} if token else {}
    logging.debug(f"Requesting files from GitHub API at: {api_url}")
    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        file_urls = [f"https://raw.githubusercontent.com/{repo_full_name}/{branch}/{file['path']}"
                     for file in response.json().get('tree', []) if file['type'] == 'blob']
        logging.debug("Successfully fetched file URLs")
        return file_urls
    else:
        logging.error(f"Failed to fetch files with status code {response.status_code}: {response.json()}")
        return {'error': 'Failed to fetch files', 'message': response.json()}

def analyze_code(file_url):
    logging.debug(f"Fetching content from GitHub for analysis at URL: {file_url}")
    try:
        file_content = requests.get(file_url).text
        full_prompt = f"Explain the purpose of the following code:\n\n{file_content}"
        logging.debug("Sending content to Ollama LLM for analysis")
        response = ollama.chat(
            model="qwen2.5-coder:14b",
            messages=[{
                'role': 'user',
                'content': full_prompt
            }]
        )
        if response:
            logging.debug("Received response from Ollama LLM")
            return {"response": response.get('message', 'No response from model')}
        else:
            logging.error("No response received from Ollama LLM")
            return {"error": "Analysis failed", "message": "No response from Ollama LLM"}
    except Exception as e:
        logging.error(f"Error during analysis: {e}")
        return {"error": "Exception occurred", "message": str(e)}


if __name__ == "__main__":
    print(f"Serving static files from: {app.static_folder}")
    print(f"Absolute path: {os.path.abspath(app.static_folder)}")
    app.run(debug=True)