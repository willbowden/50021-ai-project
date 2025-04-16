const FLASK_API_PROCESS_URL = "http://127.0.0.1:5000/process_tweet";

// --- Listener for Messages from Content Script ---
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    // Expecting { action: "processTweetText", text: tweetText, statusId: tweetStatusId }
    if (request.action === "processTweetText" && request.statusId) {
        console.log(`Background received text for Status ID ${request.statusId}:`, request.text.substring(0, 50) + "...");
        const tweetText = request.text;
        const statusId = request.statusId; // Store the Status ID

        // Acknowledge receipt immediately
        sendResponse({ status: "Text and Status ID received by background, processing..." });

        // Call the Flask API (Flask doesn't need the Status ID)
        fetch(FLASK_API_PROCESS_URL, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ tweet_text: tweetText }) // Only send text to Flask
        })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! Status: ${response.status} for Status ID ${statusId}`);
            }
            return response.json(); // Expecting { decision: 0|1, original_text: "..." }
        })
        .then(data => {
            console.log(`Received decision ${data.decision} from Flask API for Status ID ${statusId}`);
            if (data && typeof data.decision !== 'undefined' && typeof data.original_text !== 'undefined') {
                // Send the decision data AND the Status ID back to the content script
                if (sender.tab && sender.tab.id) {
                    chrome.tabs.sendMessage(sender.tab.id, {
                        action: "tweetProcessingResult",
                        resultData: {
                            decision: data.decision,
                            original_text: data.original_text, // Keep for potential logging
                            statusId: statusId // Pass the Status ID back
                        }
                    }, (response) => {
                         if (chrome.runtime.lastError) {
                            console.warn(`Could not send processing result back to content script (Status ID ${statusId}):`, chrome.runtime.lastError.message);
                         } else {
                            // console.log(`Content script acknowledged result for Status ID ${statusId}:`, response);
                         }
                    });
                } else {
                     console.error("Sender tab ID not found when trying to send processing result back.");
                }
            } else {
                 console.error(`Decision or original text not found in API response for Status ID ${statusId}:`, data);
            }
        })
        .catch(error => {
            console.error(`Error calling Flask API for Status ID ${statusId}:`, error);
            // Inform the content script about the error, including the Status ID
             if (sender.tab && sender.tab.id) {
                 chrome.tabs.sendMessage(sender.tab.id, {
                     action: "tweetProcessingResult",
                     error: `Error processing tweet: ${error.message}`,
                     statusId: statusId // Include Status ID in error message
                 });
             }
        });

        // Return true to indicate you wish to send a response asynchronously
        return true;
    }
});

console.log("Tweet Random Decision Background Script Loaded (Status ID Relay Mode).");
