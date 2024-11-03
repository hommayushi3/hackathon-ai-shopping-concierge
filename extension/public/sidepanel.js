// Configuration
const API_URL = 'http://localhost:8081/get_preferences';
const UPDATE_INTERVAL = 5000; // Poll every 5 seconds

// Store references to DOM elements
const sections = {
    personalDetails: document.getElementById('personal-details'),
    stylePreferences: document.getElementById('style-preferences'),
    colorPreferences: document.getElementById('color-preferences')
};

// Function to update the UI with new preferences
function updateUI(data) {
    if (data.personal_details) {
        sections.personalDetails.innerText = data.personal_details;
    }
    
    if (data.style_preferences) {
        sections.stylePreferences.innerText = data.style_preferences;
    }
    
    if (data.color_preferences) {
        sections.colorPreferences.innerText = data.color_preferences;
    }
}

// Function to fetch updates from the API
async function fetchUpdates() {
    try {
        const response = await fetch(API_URL);
        const data = await response.json();
        console.log('Fetched updates:', data);
        updateUI(data);
    } catch (error) {
        console.error('Error fetching updates:', error);
    }
}

// Initial fetch and setup polling
fetchUpdates();
setInterval(fetchUpdates, UPDATE_INTERVAL);
