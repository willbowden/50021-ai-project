/**
 * content.js - Uses Twitter's Status ID for robust state tracking and highlighting.
 * Applies persistent highlight using inline styles. Highlight persists off-screen.
 * Remembers decisions and highlights/re-highlights if decision is 1.
 * Logs the decision to the console.
 * Triggered by debounced scroll/mutation events.
 */
console.log("Tweet Random Highlighter Content Script Loaded (Scroll-Based / Persistent Off-Screen Mode).");

// --- State Management ---
// Track Status IDs already sent to avoid duplicates
const processedStatusIds = new Set(); // Set<string>
// Store the decisions received from the API (Map: statusId -> 0 | 1)
const tweetDecisions = new Map(); // Map<string, 0|1>
// Keep track of highlighted elements by Status ID
const highlightedElementsByStatusID = new Map(); // Map<string, HTMLElement>
let debounceTimer = null;
const DEBOUNCE_DELAY = 100; // ms delay


// --- Highlight Management ---
/**
 * Removes highlight (inline styles) for a specific tweet Status ID.
 * Still needed for Decision 0, errors, and unload cleanup.
 * @param {string} statusId - The unique Status ID of the tweet.
 */
function removeHighlightByStatusId(statusId) {
    if (highlightedElementsByStatusID.has(statusId)) {
        const element = highlightedElementsByStatusID.get(statusId);
        if (element && document.contains(element)) {
             element.style.removeProperty('outline');
             element.style.removeProperty('outline-offset');
             element.style.removeProperty('background-color');
             // console.log(`Removed inline highlight for Status ID: ${statusId}`);
        }
        highlightedElementsByStatusID.delete(statusId); // Untrack
    }
     // Fallback: Find element by Status ID again and ensure styles are removed
     const tweetElement = findTweetElementByStatusId(statusId);
     if (tweetElement) {
         tweetElement.style.removeProperty('outline');
         tweetElement.style.removeProperty('outline-offset');
         tweetElement.style.removeProperty('background-color');
     }
}

/**
 * Applies highlight for a specific tweet element and Status ID using inline styles.
 * @param {HTMLElement} element
 * @param {string} statusId - The unique Status ID of the tweet.
 */
function applyHighlightByStatusId(element, statusId) {
    if (!element || !statusId) return;

    // Apply styles directly using setProperty with !important priority
    element.style.setProperty('outline', '3px solid rgba(255, 0, 0, 0.8)', 'important');
    element.style.setProperty('outline-offset', '1px', 'important');
    element.style.setProperty('background-color', 'rgba(255, 0, 0, 0.07)', 'important');

    // Ensure it's tracked
    if (!highlightedElementsByStatusID.has(statusId) || highlightedElementsByStatusID.get(statusId) !== element) {
         highlightedElementsByStatusID.set(statusId, element);
         // console.log(`Applied/Confirmed inline highlight for Status ID: ${statusId}`);
    }
}

// --- Tweet Finding/Text/ID Extraction ---
function findVisibleTweetElements() {
    const tweetSelector = 'article[data-testid="tweet"]';
    const allTweets = document.querySelectorAll(tweetSelector);
    const visibleTweets = [];
    allTweets.forEach(tweet => {
        const rect = tweet.getBoundingClientRect();
        const isVerticallyVisible = rect.top < window.innerHeight && rect.bottom > 0;
        if (isVerticallyVisible) {
            visibleTweets.push(tweet);
        }
    });
    return visibleTweets;
}

function getTweetText(tweetElement) {
    if (!tweetElement) return null;
    const textElement = tweetElement.querySelector('div[data-testid="tweetText"]');
    return textElement ? textElement.innerText?.trim() : null;
}

/**
 * Extracts the Twitter Status ID from a tweet element.
 * Looks for a link containing '/status/' and extracts the trailing numbers.
 * @param {HTMLElement} tweetElement
 * @returns {string | null} The status ID string or null if not found.
 */
function getTweetStatusId(tweetElement) {
    if (!tweetElement) return null;
    const links = tweetElement.querySelectorAll('a[href*="/status/"]');
    for (let link of links) {
        const href = link.getAttribute('href');
        const match = href?.match(/\/status\/(\d+)/);
        if (match && match[1]) {
            const linkText = link.innerText.trim();
            const isLikelyTimestampLink = link.querySelector('time') || /^\d+m$|^\d+h$|^\d+s$|^[A-Za-z]{3}\s\d+|^[A-Za-z]{3}\s\d+,\s\d{4}/.test(linkText);
            if (isLikelyTimestampLink || links.length === 1) {
                 return match[1];
            }
        }
    }
    return null;
}


/**
 * Finds a tweet element by its unique Twitter Status ID. Searches all tweets.
 * @param {string} statusId
 * @returns {HTMLElement | null}
 */
function findTweetElementByStatusId(statusId) {
    if (!statusId) return null;
    // Check tracked elements first for efficiency
    if (highlightedElementsByStatusID.has(statusId)) {
        const trackedElement = highlightedElementsByStatusID.get(statusId);
        if (trackedElement && document.contains(trackedElement)) { return trackedElement; }
        else { highlightedElementsByStatusID.delete(statusId); } // Clean up tracking if element lost
    }
    // Search all tweet articles if not found in tracking
     const allTweets = document.querySelectorAll('article[data-testid="tweet"]');
      for (let tweetElement of allTweets) {
         const links = tweetElement.querySelectorAll(`a[href*="/status/${statusId}"]`);
         if (links.length > 0) {
              for (let link of links) {
                 const href = link.getAttribute('href');
                 const match = href?.match(/\/status\/(\d+)/);
                 if (match && match[1] === statusId) return tweetElement;
              }
         }
      }
    return null; // Not found
}


// --- Core Logic ---
/**
 * Finds all visible tweets. Uses Status ID for tracking.
 * If a decision is known, applies it using inline styles.
 * If the tweet is new (by Status ID), sends it for processing.
 */
function processVisibleTweets() {
    const visibleTweets = findVisibleTweetElements();
    // const currentlyVisibleStatusIds = new Set(); // No longer needed for cleanup loop

    visibleTweets.forEach(tweetElement => {
        const statusId = getTweetStatusId(tweetElement);

        if (statusId) {
            // currentlyVisibleStatusIds.add(statusId); // No longer needed for cleanup loop

            // 1. Check if we already have a decision stored for this tweet Status ID
            if (tweetDecisions.has(statusId)) {
                const storedDecision = tweetDecisions.get(statusId);
                // Apply the stored decision visually using inline styles
                if (storedDecision === 1) {
                    applyHighlightByStatusId(tweetElement, statusId);
                } else {
                    // Ensure highlight is removed if decision is 0
                    removeHighlightByStatusId(statusId);
                }
            }
            // 2. Else, check if it's already been sent (waiting for result)
            else if (processedStatusIds.has(statusId)) {
                // Waiting for result. Do nothing here.
            }
            // 3. Else, it's a new tweet (by Status ID) we haven't processed yet
            else {
                 const tweetText = getTweetText(tweetElement);
                 if (tweetText) { // Only process if we have text
                    // console.log(`Processing new tweet with Status ID ${statusId}:`, tweetText.substring(0, 100) + "...");
                    processedStatusIds.add(statusId); // Mark Status ID as sent

                    // Send the found text AND the Status ID to the background script
                    chrome.runtime.sendMessage({ action: "processTweetText", text: tweetText, statusId: statusId }, (response) => {
                         if (chrome.runtime.lastError) {
                            console.warn(`Error sending message for Status ID ${statusId}:`, chrome.runtime.lastError.message);
                            processedStatusIds.delete(statusId); // Allow retry
                        } else {
                            // console.log(`Background ack send for Status ID ${statusId}:`, response);
                        }
                    });
                 }
            }
        }
    });

    // *** Cleanup loop REMOVED ***
    /*
    // Cleanup highlights for tweets that are tracked (by Status ID) but *no longer visible*
    highlightedElementsByStatusID.forEach((element, statusId) => {
        if (!currentlyVisibleStatusIds.has(statusId)) {
             // This Status ID is highlighted but not currently visible
             removeHighlightByStatusId(statusId); // Untrack and remove styles
        }
    });
    */
}

// --- Debounce Function (Same as before) ---
function debounce(func, delay) {
    return function(...args) {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
            func.apply(this, args);
        }, delay);
    };
}

// --- Listener for Processed Results from Background ---
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    // Expecting { action: "tweetProcessingResult", resultData: { decision: ..., statusId: ... }, error: ... }
    if (request.action === "tweetProcessingResult") {
        const statusId = request.resultData?.statusId || request.statusId; // Get Status ID from result or error

        if (!statusId) {
            console.error("Received result/error without a Status ID:", request);
            sendResponse({ status: "Error: Missing Status ID" });
            return true;
        }

        if (request.error) {
            console.error(`Error reported from background/API for Status ID ${statusId}:`, request.error);
            // Remove from processed set so it can be retried if needed
            processedStatusIds.delete(statusId);
            // Remove any potential highlight
            removeHighlightByStatusId(statusId);
            sendResponse({ status: "Error acknowledged by content script" });
            return true;
        }

        if (request.resultData && typeof request.resultData.decision !== 'undefined') {
            const decision = request.resultData.decision;
            const originalText = request.resultData.original_text; // Still useful for logging

            console.log(`API Decision: ${decision} for Status ID ${statusId} (Text: ${originalText.substring(0, 50)}...)`);

            // Store the decision using the Status ID
            tweetDecisions.set(statusId, decision);

            // Find the element *now* using the Status ID to apply initial highlight/removal
            // We might need to search all elements, not just visible ones, if result arrives late
            const tweetElement = findTweetElementByStatusId(statusId);

            if (tweetElement) {
                if (decision === 1) {
                    applyHighlightByStatusId(tweetElement, statusId); // Use Status ID-based function
                } else {
                    removeHighlightByStatusId(statusId); // Use Status ID-based function
                }
            } else {
                 // Element not found when result arrived, decision is stored.
                 // If we were tracking a highlight for it, remove that tracking.
                 removeHighlightByStatusId(statusId);
            }
            sendResponse({ status: "Result processed and stored by content script" });

        } else {
             console.error(`Invalid result data received from background for Status ID ${statusId}:`, request);
             sendResponse({ status: "Invalid data received by content script" });
        }
    }
    return true;
});


// --- Event Listeners & Initial Run ---
const debouncedCheck = debounce(processVisibleTweets, DEBOUNCE_DELAY);
window.addEventListener('scroll', debouncedCheck, { passive: true });
const observerTarget = document.body;
const observerConfig = { childList: true, subtree: true };
const mutationObserver = new MutationObserver(debouncedCheck);
if (observerTarget) {
    mutationObserver.observe(observerTarget, observerConfig);
    console.log("MutationObserver started.");
} else { console.warn("Could not find observer target (document.body)."); }
setTimeout(processVisibleTweets, 750); // Initial check

// --- Cleanup on Unload ---
window.addEventListener('unload', () => {
    console.log("Tweet Random Highlighter Content Script: Cleaning up listeners.");
    window.removeEventListener('scroll', debouncedCheck);
    if (mutationObserver) mutationObserver.disconnect();
    clearTimeout(debounceTimer);
    // Clear state on unload
    processedStatusIds.clear();
    tweetDecisions.clear();
    // Remove any remaining highlights on unload
    highlightedElementsByStatusID.forEach((element, statusId) => removeHighlightByStatusId(statusId));
    highlightedElementsByStatusID.clear();
});
