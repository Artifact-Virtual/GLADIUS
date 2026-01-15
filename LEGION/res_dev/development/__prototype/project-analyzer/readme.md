## Setup Instructions

1. **Install Python**  
    Ensure you have **Python 3.8+** installed on your system.

2. **Navigate to the Backend Directory**  
    Open your terminal and run:
    ```sh
    cd backend
    ```

3. **Install Dependencies**  
    Install the required Python packages:
    ```sh
    pip install -r requirements.txt
    ```

4. **Set Environment Variables**  
    - Create a `.env` file in the `backend` directory.
    - Add the following variables:
      - `GITHUB_TOKEN`
      - `VERTEX_PROJECT_ID`
      - `VERTEX_LOCATION`
      - `GOOGLE_APPLICATION_CREDENTIALS` (full path to your Google Cloud service account JSON key file)

    **Example:**
    ```
    GOOGLE_APPLICATION_CREDENTIALS=/Users/youruser/keys/my-vertex-ai-key.json
    ```

5. **Run the Flask App**  
    Start the server with:
    ```sh
    python app.py
    ```
    The server should start, typically at [http://localhost:5000](http://localhost:5000).