import { dataStore, filterPlaylists } from './dataStore.js';
import { decodeHtmlEntities } from './utils.js';
import { fetchUserPlaylists, sendFormData } from './api.js';
import { onPlaylistFormSubmit, onPlaylistNameConfirm, updateDataStore } from './listeners.js';


function showLoadingIndicator() {
    const loadingIndicator = document.getElementById('loading-indicator');
    loadingIndicator.style.display = 'block';
};


function hideLoadingIndicator() {
    const loadingIndicator = document.getElementById('loading-indicator');
    loadingIndicator.style.display = 'none';
};


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
};


async function submitForm(event) {
    event.preventDefault();
    showLoadingIndicator();
    document.querySelector(".result").style.display = "none";
    document.querySelector(".code").style.display = "none";
    
    const form_type = event.target.id.slice(0, event.target.id.indexOf("-form"));
  
    if (form_type === "playlist") {
      let playlist_name = document.querySelector("#playlist-input").value;
      let question = document.querySelector("#question-input").value;
      await onPlaylistFormSubmit(playlist_name, question);
    }
    
    const form_data = {
          formType: form_type,
          data: dataStore.getAllData(),
    };
  
    const updated_data_store = await sendFormData("/", form_data);
    updateDataStore(updated_data_store);
    
    hideLoadingIndicator();
};  


export function handlePlaylistNameEvent(playlistName) {
    document.getElementById('playlist-input').textContent = decodeHtmlEntities(playlistName);
};


export function handlePlaylistInfoEvent(playlistInfo) {
    if (playlistInfo) {
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
        document.getElementById('playlist-info').style.display = 'none';
    }
};


export function handleGptResponseEvent(gptResponse) {
    document.getElementById("generated-response").textContent = gptResponse;
    if (gptResponse) {
        document.querySelector(".code").style.display = "block";
    } else {
        document.querySelector(".code").style.display = "none";
    }
};


export function handleResultEvent(result) {
    if (result) {
        document.getElementById("result-text").innerHTML = result;
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


function initializeForms() {
    const forms = document.querySelectorAll('form');
    forms.forEach((form) => {
        form.addEventListener('submit', submitForm);
    });
}

function initializeCodeButtons() {
    const toggleCodeButton = document.getElementById("toggle-code-button");

    toggleCodeButton.addEventListener("click", toggleGeneratedCode);
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
    initializeCodeButtons();
    initializeSampleQuestions();
});
