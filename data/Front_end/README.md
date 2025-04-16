# Tweet Random Highlighter Extension

This project consists of a Chrome extension and a local Python Flask backend. The extension automatically scans tweets on Twitter/X, extracts a unique Status ID, and sends the tweet text to the local backend. The backend returns a random decision (0 or 1). The extension then highlights the corresponding tweet in red if the decision is 1 and remembers this decision for the duration of the page session.

## Features

* Automatic scanning of visible tweets on Twitter/X using Status IDs.
* Communication with a local Python Flask API for decision making.
* Random highlighting of tweets based on the API's response (1 = highlight, 0 = no highlight).
* State persistence within a page session (remembers decisions for tweets).
* Persistent highlighting using inline styles (resists basic hover effects).
* Debounced processing triggered by scroll/DOM mutations for performance.

## Prerequisites

* **Python 3.x:** Make sure Python 3 is installed on your system. You can download it from [python.org](https://www.python.org/).
* **pip:** Python's package installer (usually comes with Python 3).
* **Google Chrome:** The extension is designed for the Chrome browser.

## Installation

You need to set up both the backend API and the frontend Chrome extension.

### 1. Backend (Flask API)

1.  **Create Project Folder:** Create a folder for the backend code, e.g., `tweet-highlighter-backend`.
2.  **Save Backend Code:** Save the Python Flask code (the version that returns a random decision, like `flask_api_random_v1`) as `app_flask.py` inside this folder.
3.  **Navigate to Folder:** Open your terminal or command prompt and navigate into the `tweet-highlighter-backend` folder.
    ```bash
    cd path/to/tweet-highlighter-backend
    ```
4.  **Create Virtual Environment (Recommended):**
    * On macOS/Linux:
        ```bash
        python3 -m venv venv
        source venv/bin/activate
        ```
    * On Windows:
        ```bash
        python -m venv venv
        .\venv\Scripts\activate
        ```
5.  **Install Dependencies:** Install Flask and Flask-CORS.
    ```bash
    pip install Flask Flask-Cors
    ```

### 2. Frontend (Chrome Extension)

1.  **Create Extension Folder:** Create a separate folder for the extension files, e.g., `tweet-highlighter-extension`.
2.  **Save Extension Files:** Place the following files inside the `tweet-highlighter-extension` folder:
    * `manifest.json` (Use the structure from `manifest_flask_refresher_v4`, ensuring the name/description match, e.g., "Tweet Random Highlighter (Auto)", and it includes host permissions for `http://127.0.0.1:5000/`, `*://*.twitter.com/*`, `*://*.x.com/*`, and the `content_scripts` section).
    * `background.js` (Use the code from `background_script_tweet_v5`).
    * `content.js` (Use the code from `content_script_tweet_v15_faster_debounce`).
3.  **Load Extension in Chrome:**
    * Open Google Chrome and navigate to `chrome://extensions/`.
    * Enable **"Developer mode"** using the toggle switch (usually in the top-right corner).
    * Click the **"Load unpacked"** button.
    * Navigate to and select the `tweet-highlighter-extension` folder you created.
    * The extension should now appear in your list. Make sure it is enabled (toggle switch is on).

## Running the Project

1.  **Start the Backend:**
    * Open your terminal/command prompt.
    * Navigate to the backend folder (`tweet-highlighter-backend`).
    * If you used a virtual environment, activate it (`source venv/bin/activate` or `.\venv\Scripts\activate`).
    * Run the Flask application:
        ```bash
        python app_flask.py
        ```
    * You should see output indicating the server is running, likely on `http://127.0.0.1:5000/` or `http://0.0.0.0:5000/`. Keep this terminal window open while using the extension.

2.  **Use the Extension:**
    * Make sure the "Tweet Random Highlighter (Auto)" extension is enabled in `chrome://extensions/`.
    * Navigate to `twitter.com` or `x.com`.
    * Scroll the page. As tweets become visible, the extension should process them.
    * Open the Developer Console (F12 or Right-click -> Inspect -> Console tab) on the Twitter/X page to see log messages, including the `API Decision: 0` or `API Decision: 1` outputs.
    * Tweets corresponding to a decision of `1` should receive a persistent red highlight. Tweets with decision `0` should not be highlighted.
    * Highlights for "Decision 1" tweets should reappear if you scroll away and then back to them.

## How It Works

1.  **Content Script (`content.js`):** Injected automatically into Twitter/X pages.
2.  **Detection:** Uses `scroll` listeners and `MutationObserver` (debounced) to trigger checks.
3.  **Processing Visible Tweets:** The `processVisibleTweets` function finds visible tweets.
4.  **ID Extraction:** It extracts the unique Twitter Status ID for each tweet.
5.  **State Check:** It checks if the Status ID has already been processed (`processedStatusIds`) or if a decision is already stored (`tweetDecisions`).
6.  **API Call (if new):** If the tweet is new, its Status ID is added to `processedStatusIds`, and its text and Status ID are sent via `chrome.runtime.sendMessage` to the background script.
7.  **Background Script (`background.js`):** Receives the message, makes a `fetch` POST request to the local Flask API (`http://127.0.0.1:5000/process_tweet`) with the tweet text.
8.  **Flask API (`app_flask.py`):** Receives the text, generates a random 0 or 1, and returns a JSON response containing the decision and original text.
9.  **Result Handling:** The background script receives the Flask response and sends it back to the content script, including the `statusId`.
10. **State Update & Highlighting:** The content script receives the result, logs the decision, stores the decision in the `tweetDecisions` map using the `statusId`, and calls `applyHighlightByStatusId` (for decision 1) or `removeHighlightByStatusId` (for decision 0) to update the tweet's appearance using inline styles.
11. **Re-Highlighting:** When scrolling, `processVisibleTweets` checks `tweetDecisions` and re-applies highlights to visible tweets based on the stored decisions.

**Note:** Twitter/X frequently updates its website structure. This can break the selectors used to find tweets (`article[data-testid="tweet"]`), text (`div[data-testid="tweetText"]`), or Status IDs (`a[href*="/status/"]`). If the extension stops working, these selectors in `content.js` may need to be updated by inspecting the Twitter/X HTML.
