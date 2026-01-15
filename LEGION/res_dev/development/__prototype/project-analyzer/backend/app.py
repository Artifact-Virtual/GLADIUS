import os
import io
import shutil
import zipfile
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from github import Github  # PyGithub library
from google.cloud import aiplatform  # Vertex AI client
from vertexai.preview.generative_models import (
    GenerativeModel,
    Part,
    GenerationConfig,
    Tool,
    ToolCodeExecution,
)
from flask_cors import CORS  # To allow frontend to make requests

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes, adjust for production as needed

# --- Configuration ---
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
VERTEX_PROJECT_ID = os.getenv(
    "VERTEX_PROJECT_ID", "your-gcp-project-id"
)  # Replace with your GCP project ID
VERTEX_LOCATION = os.getenv("VERTEX_LOCATION", "us-central1")  # Or your desired region
FLASK_RUN_PORT = int(os.getenv("FLASK_RUN_PORT", 5000))

# Initialize Vertex AI client
try:
    aiplatform.init(project=VERTEX_PROJECT_ID, location=VERTEX_LOCATION)
    gemini_pro_model = GenerativeModel(
        "gemini-2.0-flash"
    )  # Use gemini-2.0-flash as per instructions
    print("Vertex AI client initialized successfully.")
except Exception as e:
    print(f"Error initializing Vertex AI client: {e}")
    print(
        "Please ensure GOOGLE_APPLICATION_CREDENTIALS environment variable is set correctly and points to your service account key file."
    )
    gemini_pro_model = None  # Set to None if initialization fails

# Initialize GitHub client
g = Github(GITHUB_TOKEN)

# --- Helper Functions for Code Analysis ---


def analyze_code_with_gemini(
    code_content: str, user_prompt: str, is_chart_request: bool = False
):
    """Sends code content to Gemini for analysis or chart data generation."""
    if not gemini_pro_model:
        return {
            "error": "Vertex AI model not initialized. Check backend logs for details."
        }

    chat_history = []
    system_instruction = """
        You are an expert code analysis assistant.
        When asked to provide metrics or charts based on the provided code snippet, generate a JSON array of chart configurations.
        Each chart object should strictly follow this schema. If you cannot generate meaningful charts, return an empty array [].
        Ensure all string values are properly escaped for JSON.

        Schema for chart objects:
        [
          {
            "id": "unique-chart-id",
            "type": "bar" | "pie" | "line",
            "title": "A descriptive title for the chart (e.g., 'Lines per Function', 'File Type Distribution')",
            "description": "A brief explanation of what the chart represents.",
            "data": [
              // Array of data objects. Keys depend on chart type.
              // For 'bar'/'line': {"name": "Category", "value": 10},
              // For 'pie': {"name": "Slice Name", "value": 5}
            ],
            "dataKeys": { // Specifies which keys in 'data' map to chart elements
              "name": "name", // For XAxis (bar/line) or slice name (pie)
              "value": "value" // For YAxis (bar/line) or slice value (pie)
            },
            "colors": ["#hexcolor1", "#hexcolor2"] // Optional: specific colors for slices/bars
          }
        ]

        When analyzing code for charts, consider metrics like:
        - Line counts (total, per file, per function, per component)
        - File type distribution
        - Number of functions, classes, components
        - Distribution of comments, empty lines
        - Cyclomatic complexity (if inferable)
        - Dependencies (simple counts if inferable)

        For any other questions not related to chart generation, respond conversationally.
    """

    # Add the user's prompt and code content to the chat history
    chat_history.append(
        Part.from_text(
            f"Code snippet to analyze:\n```\n{code_content}\n```\n\nUser's request: {user_prompt}"
        )
    )

    generation_config = GenerationConfig()
    if is_chart_request:
        generation_config.response_mime_type = "application/json"
        generation_config.response_schema = {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "id": {"type": "STRING"},
                    "type": {"type": "STRING", "enum": ["bar", "pie", "line"]},
                    "title": {"type": "STRING"},
                    "description": {"type": "STRING"},
                    "data": {"type": "ARRAY", "items": {"type": "OBJECT"}},
                    "dataKeys": {
                        "type": "OBJECT",
                        "properties": {
                            "name": {"type": "STRING"},
                            "value": {"type": "STRING"},
                        },
                        "required": ["name", "value"],
                    },
                    "colors": {"type": "ARRAY", "items": {"type": "STRING"}},
                },
                "required": ["id", "type", "title", "data", "dataKeys", "description"],
            },
        }

    try:
        response = gemini_pro_model.generate_content(
            chat_history,
            generation_config=generation_config,
            system_instruction=system_instruction,
        )
        return response.text
    except Exception as e:
        print(f"Error calling Vertex AI: {e}")
        return {"error": f"Failed to get response from Vertex AI: {e}"}


# --- Backend Routes ---


@app.route("/api/chat-analyze", methods=["POST"])
def chat_analyze():
    """
    Endpoint for general chat analysis or chart data generation from a code snippet.
    Expects JSON: {"code_snippet": "...", "prompt": "...", "is_chart_request": true/false}
    """
    data = request.json
    code_snippet = data.get("code_snippet", "")
    prompt = data.get("prompt", "Analyze the provided code.")
    is_chart_request = data.get("is_chart_request", False)

    if not code_snippet:
        return jsonify({"error": "No code snippet provided for analysis."}), 400

    ai_response = analyze_code_with_gemini(code_snippet, prompt, is_chart_request)

    if isinstance(ai_response, dict) and "error" in ai_response:
        return jsonify(ai_response), 500

    # If it was a chart request, the response is already JSON from AI.
    # Otherwise, it's plain text.
    if is_chart_request:
        try:
            return jsonify(
                {"type": "charts", "data": ai_response}
            )  # Vertex AI response is already parsed JSON
        except Exception as e:
            return (
                jsonify(
                    {"type": "text", "data": f"Backend failed to parse chart data: {e}"}
                ),
                500,
            )
    else:
        return jsonify({"type": "text", "data": ai_response}), 200


@app.route("/api/analyze-github-repo", methods=["POST"])
def analyze_github_repo():
    """
    Endpoint to clone and analyze a GitHub repository.
    Expects JSON: {"repo_url": "...", "prompt": "...", "is_chart_request": true/false}
    """
    data = request.json
    repo_url = data.get("repo_url")
    prompt = data.get("prompt", "Analyze this repository.")
    is_chart_request = data.get("is_chart_request", False)

    if not repo_url:
        return jsonify({"error": "GitHub repository URL is required."}), 400

    if not GITHUB_TOKEN:
        return (
            jsonify(
                {
                    "error": "GitHub token not configured in backend. Cannot clone private repositories."
                }
            ),
            500,
        )

    repo_dir = (
        f"cloned_repos/{repo_url.split('/')[-1]}"  # Unique directory for each repo
    )

    try:
        # Clean up previous clone if it exists
        if os.path.exists(repo_dir):
            shutil.rmtree(repo_dir)

        # Clone the repository
        # For private repos, you'd need authentication in the URL, e.g.,
        # git clone https://oauth2:<GITHUB_TOKEN>@github.com/user/repo.git
        repo_to_clone = repo_url
        if "github.com" in repo_url and GITHUB_TOKEN:
            # Inject token for private repos or rate limit bypass for public ones
            # This is a simplified example, consider PyGithub for more robust API interaction
            # For actual git clone, you'd need the git CLI installed on the server.
            # Using PyGithub's direct clone:
            from git import Repo

            Repo.clone_from(
                f"https://oauth2:{GITHUB_TOKEN}@{repo_url.replace('https://', '')}",
                repo_dir,
            )
        else:
            return (
                jsonify(
                    {"error": "Invalid GitHub URL or missing token for private repo."}
                ),
                400,
            )

        # Read relevant files (e.g., all .js, .py, .java files)
        full_codebase_content = ""
        file_count = 0
        for root, _, files in os.walk(repo_dir):
            for file in files:
                if file.endswith(
                    (
                        ".js",
                        ".py",
                        ".java",
                        ".ts",
                        ".jsx",
                        ".tsx",
                        ".html",
                        ".css",
                        ".md",
                    )
                ):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            # Limit file size for individual AI prompts if needed
                            content = f.read(50000)  # Read up to 50KB per file
                            full_codebase_content += f"\n--- File: {file_path.replace(repo_dir + os.sep, '')} ---\n{content}\n"
                            file_count += 1
                            if (
                                len(full_codebase_content) > 200000
                            ):  # Max 200KB of combined code for demo
                                full_codebase_content += (
                                    "\n... (truncated due to size limit) ...\n"
                                )
                                break  # Stop reading files if overall limit reached
                    except Exception as e:
                        print(f"Could not read file {file_path}: {e}")
            if len(full_codebase_content) > 200000:
                break

        if not full_codebase_content:
            return (
                jsonify(
                    {"error": "No recognizable code files found or content too large."}
                ),
                400,
            )

        # Here's where you'd integrate more sophisticated static analysis
        # For this demo, we'll send the concatenated code to Vertex AI
        ai_response = analyze_code_with_gemini(
            full_codebase_content, prompt, is_chart_request
        )

        if isinstance(ai_response, dict) and "error" in ai_response:
            return jsonify(ai_response), 500

        if is_chart_request:
            try:
                return (
                    jsonify({"type": "charts", "data": ai_response}),
                    200,
                )  # Vertex AI response is already parsed JSON
            except Exception as e:
                return (
                    jsonify(
                        {
                            "type": "text",
                            "data": f"Backend failed to parse chart data: {e}",
                        }
                    ),
                    500,
                )
        else:
            return jsonify({"type": "text", "data": ai_response}), 200

    except Exception as e:
        print(f"Error during GitHub repository analysis: {e}")
        return jsonify({"error": f"Failed to analyze GitHub repository: {e}"}), 500
    finally:
        # Clean up cloned repository
        if os.path.exists(repo_dir):
            shutil.rmtree(repo_dir)


@app.route("/api/analyze-zip-file", methods=["POST"])
def analyze_zip_file():
    """
    Endpoint to analyze a ZIP file.
    Expects form-data with "zip_file"
    """
    if "zip_file" not in request.files:
        return jsonify({"error": "No zip file provided."}), 400

    zip_file = request.files["zip_file"]
    prompt = request.form.get("prompt", "Analyze this zipped code.")
    is_chart_request = request.form.get("is_chart_request", "false").lower() == "true"

    if zip_file.filename == "":
        return jsonify({"error": "No selected file."}), 400

    if not zip_file.filename.endswith(".zip"):
        return (
            jsonify({"error": "Invalid file type. Only ZIP files are supported."}),
            400,
        )

    # Process the ZIP file in memory or extract to temp directory
    temp_dir = "temp_zip_extract"
    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)

    try:
        with zipfile.ZipFile(io.BytesIO(zip_file.read()), "r") as z:
            z.extractall(temp_dir)

        full_codebase_content = ""
        file_count = 0
        for root, _, files in os.walk(temp_dir):
            for file in files:
                if file.endswith(
                    (
                        ".js",
                        ".py",
                        ".java",
                        ".ts",
                        ".jsx",
                        ".tsx",
                        ".html",
                        ".css",
                        ".md",
                    )
                ):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read(50000)  # Read up to 50KB per file
                            full_codebase_content += f"\n--- File: {file_path.replace(temp_dir + os.sep, '')} ---\n{content}\n"
                            file_count += 1
                            if (
                                len(full_codebase_content) > 200000
                            ):  # Max 200KB of combined code for demo
                                full_codebase_content += (
                                    "\n... (truncated due to size limit) ...\n"
                                )
                                break
                    except Exception as e:
                        print(f"Could not read file {file_path}: {e}")
            if len(full_codebase_content) > 200000:
                break

        if not full_codebase_content:
            return (
                jsonify(
                    {
                        "error": "No recognizable code files found in ZIP or content too large."
                    }
                ),
                400,
            )

        ai_response = analyze_code_with_gemini(
            full_codebase_content, prompt, is_chart_request
        )

        if isinstance(ai_response, dict) and "error" in ai_response:
            return jsonify(ai_response), 500

        if is_chart_request:
            try:
                return jsonify({"type": "charts", "data": ai_response}), 200
            except Exception as e:
                return (
                    jsonify(
                        {
                            "type": "text",
                            "data": f"Backend failed to parse chart data: {e}",
                        }
                    ),
                    500,
                )
        else:
            return jsonify({"type": "text", "data": ai_response}), 200

    except Exception as e:
        print(f"Error processing ZIP file: {e}")
        return jsonify({"error": f"Failed to analyze ZIP file: {e}"}), 500
    finally:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)


if __name__ == "__main__":
    # Create directory for cloned repos if it doesn't exist
    os.makedirs("cloned_repos", exist_ok=True)
    app.run(debug=True, port=FLASK_RUN_PORT)  # debug=True only for development
