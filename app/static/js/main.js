import { dataStore, filterPlaylists } from './dataStore.js';
import { decodeHtmlEntities, extractPlaylistIdFromLink } from './utils.js';
import { fetchUserPlaylists, resolveShortUrl, sendFormData } from './api.js';
import { onPlaylistFormSubmit, onPlaylistNameConfirm, updatePlaylistInfo, updateDataStore } from './listeners.js';


function showLoadingIndicator() {
    const loadingIndicator = document.getElementById('loading-indicator');
    loadingIndicator.style.display = 'block';
};


function hideLoadingIndicator() {
    const loadingIndicator = document.getElementById('loading-indicator');
    loadingIndicator.style.display = 'none';
};


export function hideGeneratedCode() {
    document.querySelector(".code").style.display = "none";
}


export function hideResult() {
    document.querySelector(".result").style.display = "none";
}


function initializePlaylistAutocomplete() {
    const playlistInputContainer = document.getElementById('playlist-autocomplete-container');
  
    accessibleAutocomplete({
        element: playlistInputContainer,
        id: 'playlist-input',
        source: (query, populateResults) => {
        if (query.length > 0) {
            const filteredPlaylists = filterPlaylists(query);
            populateResults(filteredPlaylists.map((playlist) => playlist.name));
        } else {
            populateResults();
        }},
        placeholder: 'Enter your playlist name exactly.',
        onConfirm: onPlaylistNameConfirm,
        name: 'playlist_name',
        required: true,
        showNoOptionsFound: false,
        displayMenu: 'overlay',
        cssNamespace: 'custom-autocomplete',
    });
  
    const playlistInput = document.getElementById('playlist-input');
    playlistInput.classList.add('playlist-search-input');
    playlistInput.addEventListener('input', () => document.getElementById('playlist-link-input').value = '');
};


async function submitForm(event) {
    event.preventDefault();
    hideGeneratedCode();
    hideResult();
    showLoadingIndicator();
    
    const formType = event.target.id.slice(0, event.target.id.indexOf("-form"));
  
    if (formType === "playlist") {
        let playlistName = document.querySelector("#playlist-input").value;
        let question = document.querySelector("#question-input").value;
        await onPlaylistFormSubmit(playlistName, question);
    }
    
    const form_data = {
          formType: formType,
          data: dataStore.getAllData(),
    };
  
    const updatedDataStore = await sendFormData("/", form_data);
    updateDataStore(updatedDataStore);
    
    if (formType === "code") {
        const latestGptResponse = dataStore.get("gptResponses")?.slice(-1)[0];
        handleResultEvent(latestGptResponse.result, latestGptResponse.error);
        if (latestGptResponse.error) {
            document.getElementById("debug-button").style.display = "block";
        } else {
            document.getElementById("debug-button").style.display = "none";
        }
    };
    
    hideLoadingIndicator();
};


async function handleSearchButtonClick(event) {
    event.preventDefault();

    const playlistLink = document.getElementById('playlist-link-input').value;
    const extracted = extractPlaylistIdFromLink(playlistLink);

    if (extracted) {
        const { id, isShortUrl } = extracted;
        const playlistId = isShortUrl ? await resolveShortUrl(playlistLink) : id;

        if (playlistId) {
            await updatePlaylistInfo(playlistId);
            const playlistName = dataStore.get('playlistName');
            const playlistInput = document.getElementById('playlist-input');
            playlistInput.value = playlistName;
        } else {
            alert('Failed to resolve the Spotify playlist ID.');
        }
    } else {
        alert('Invalid Spotify playlist link. Please check the link and try again.');
    }
};



export function handlePlaylistNameEvent(playlistName) {
    document.getElementById('playlist-input').textContent = decodeHtmlEntities(playlistName);
};


export function handlePlaylistInfoEvent(playlistInfo) {
    if (playlistInfo) {
        document.getElementById('playlist-link-input').value = playlistInfo.external_urls.spotify;
        document.getElementById('playlist-name').innerHTML = `<a href="${playlistInfo.external_urls.spotify}" target="_blank">
            ${decodeHtmlEntities(playlistInfo.name)}</a>`;
        document.getElementById('playlist-image').src = playlistInfo.images[0].url || "";
        document.getElementById('playlist-description').textContent = decodeHtmlEntities(playlistInfo.description) 
            || "No description provided.";
        document.getElementById('author-name').textContent = decodeHtmlEntities(playlistInfo.owner.display_name) 
            || "Unavailable";
        document.getElementById('author-name').href = playlistInfo.owner.external_urls.spotify || "#";
        document.getElementById('playlist-info').style.display = 'block';
    } else {
        document.getElementById('playlist-link-input').value = '';
        document.getElementById('playlist-info').style.display = 'none';
    }
};


export function handleGptResponseEvent(gptResponses) {
    if (gptResponses && gptResponses.length > 0) {
        const latestGptResponse = gptResponses[gptResponses.length - 1];
        document.getElementById("generated-response").textContent = latestGptResponse.response;
        document.querySelector(".code").style.display = "block";
    } else {
        document.getElementById("generated-response").textContent = '';
        document.querySelector(".code").style.display = "none";
    }
};


export function handleResultEvent(result, error) {
    if (result || error) {
        document.getElementById("result-text").innerHTML = result || error;
        document.querySelector(".result").style.display = "block";
        document.querySelector(".code").style.display = "none";
        document.getElementById("toggle-code-button").checked = false;
    } else {
        document.querySelector(".result").style.display = "none";
    }
    updateToggleButtonText();
};


function updateToggleButtonText() {
    const codeDiv = document.querySelector(".code");
    const toggleCodeButton = document.getElementById("toggle-code-button");
    if (codeDiv.style.display === "block") {
        toggleCodeButton.textContent = "Hide generated code";
    } else {
        toggleCodeButton.textContent = "Show generated code";
    }
};


function toggleGeneratedCode() {
    const codeDiv = document.querySelector(".code");
    if (codeDiv.style.display === "block") {
        codeDiv.style.display = "none";
    } else {
        codeDiv.style.display = "block";
    }
    updateToggleButtonText();
};


async function copyToClipboard(text) {
    try {
        await navigator.clipboard.writeText(text);
    } catch (err) {
        console.error('Failed to copy text:', err);
    }
};


async function handleCopyCodeButtonClick() {
    const gptResponses = dataStore.get('gptResponses');
    if (gptResponses && gptResponses.length > 0) {
        const latestGptResponse = gptResponses[gptResponses.length - 1];
        await copyToClipboard(latestGptResponse.code);
    }
};


async function handleDebugButtonClick() {
    showLoadingIndicator();
    hideGeneratedCode();
    hideResult();

    const formData = {
        formType: "debug",
        data: dataStore.getAllData(),
    };

    const updatedDataStore = await sendFormData("/", formData);
    updateDataStore(updatedDataStore);

    hideLoadingIndicator();
}


function initializeForms() {
    const forms = document.querySelectorAll('form');
    forms.forEach((form) => {
        form.addEventListener('submit', submitForm);
    });
}

function initializeButtons() {
    const toggleCodeButton = document.getElementById("toggle-code-button");
    const searchButton = document.getElementById("url-search-button");
    const copyCodeButton = document.getElementById('copy-code-button');
    const debugCodeButton = document.getElementById('debug-button');

    toggleCodeButton.addEventListener("click", toggleGeneratedCode);
    searchButton.addEventListener("click", handleSearchButtonClick);
    copyCodeButton.addEventListener("click", handleCopyCodeButtonClick);
    debugCodeButton.addEventListener("click", handleDebugButtonClick);
}


function initializeSampleQuestions() {
    const sampleQuestions = document.querySelectorAll('.sample-question');
    sampleQuestions.forEach((sampleQuestion) => {
        sampleQuestion.addEventListener('click', (event) => {
            event.preventDefault();
            document.querySelector('input[name="question"]').value = event.target.textContent;
        });
    });
}


document.addEventListener("DOMContentLoaded", () => {
    fetchUserPlaylists();
    initializeForms();
    initializePlaylistAutocomplete();
    initializeButtons();
    initializeSampleQuestions();
});
