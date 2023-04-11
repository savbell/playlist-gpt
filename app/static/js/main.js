let playlists = [];

async function fetchPlaylists() {
  const response = await fetch("/playlists");
  playlists = await response.json();
}

function filterPlaylists(input) {
  return playlists.filter((playlist) => playlist.name.toLowerCase().startsWith(input.toLowerCase()));
}

function showLoadingIndicator() {
  const loadingIndicator = document.getElementById('loading-indicator');
  loadingIndicator.style.display = 'block';
}

function hideLoadingIndicator() {
  const loadingIndicator = document.getElementById('loading-indicator');
  loadingIndicator.style.display = 'none';
}

function updatePlaylistUI(playlistInfo) {
  document.getElementById('playlist-name').innerHTML = `<a href="${playlistInfo.external_urls.spotify}" target="_blank">
    ${decodeHtmlEntities(playlistInfo.name)}</a>`;
  document.getElementById('playlist-image').src = playlistInfo.images[0].url || "";
  document.getElementById('playlist-description').textContent = decodeHtmlEntities(playlistInfo.description) 
    || "No description provided.";
  document.getElementById('author-name').textContent = decodeHtmlEntities(playlistInfo.owner.display_name) 
    || "Unavailable";
  document.getElementById('author-name').href = playlistInfo.owner.external_urls.spotify || "#";
  document.getElementById('playlist-info').style.display = 'block';
}

async function displayPlaylistInfo(playlistId) {
  const response = await fetch(`/playlist-info/${playlistId}`);
  const playlistInfo = await response.json();
  updatePlaylistUI(playlistInfo);
}

function updateUI(data) {
  const { result, playlist_name, gpt_response, playlist_id } = data;

  if (gpt_response) {
    document.getElementById("generated-response").textContent = gpt_response;
    document.getElementById("hidden-playlist-name").value = playlist_name;
    document.getElementById("hidden-gpt-response").value = gpt_response;
    document.querySelector(".code").style.display = "block";
  }
  if (result) {
    document.getElementById("result-text").innerHTML = result;
    document.querySelector(".result").style.display = "block";
    document.querySelector(".code").style.display = "none";
    document.getElementById("toggle-code-button").checked = false;
  }
  if (playlist_id) {
    displayPlaylistInfo(playlist_id);
  }
  updateToggleButtonText();
}

async function sendFormData(url, data) {
  const response = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(data),
  });
  return await response.json();
}

async function submitForm(event) {
  event.preventDefault();
  showLoadingIndicator();

  document.querySelector(".result").style.display = "none";
  document.querySelector(".code").style.display = "none";

  const formType = event.target.id.slice(0, event.target.id.indexOf("-form"));

  let playlist_name = document.querySelector("#playlist-input").value;

  // Check if the playlist is one of the user's playlists or a new search
  const isUserPlaylist = playlists.some((playlist) => playlist.id === playlist_name);
  if (!isUserPlaylist && formType === "playlist") {
    const searchResponse = await fetch(`/search-playlist/${encodeURIComponent(playlist_name)}`);
    const searchResult = await searchResponse.json();
    if (searchResult && searchResult.id) {
      playlist_name = searchResult.id;
      updatePlaylistUI(searchResult);
    }
  }

  const formData = {
    form_type: formType,
    playlist_name: playlist_name,
    question: document.querySelector('input[name="question"]').value,
    gpt_response: formType === "code" ? document.getElementById("generated-response").textContent : "",
  };

  const result = await sendFormData("/", formData);

  hideLoadingIndicator();
  updateUI(result);
}

function initializeForms() {
  const forms = document.querySelectorAll('form');
  forms.forEach((form) => {
    form.addEventListener('submit', submitForm);
  });
}

function decodeHtmlEntities(str) {
  const textarea = document.createElement('textarea');
  textarea.innerHTML = str;
  return textarea.value;
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
      }
    },    
    placeholder: 'Enter your playlist name exactly.',
    onConfirm: (value) => {
      const selectedPlaylist = playlists.find((playlist) => playlist.name === value);
      if (selectedPlaylist) {
        playlistInput.value = selectedPlaylist.id;
        displayPlaylistInfo(selectedPlaylist.id);
      } else {
        playlistInput.value = "";
      }
    },
    name: 'playlist_name',
    required: true,
    showNoOptionsFound: false,
    displayMenu: 'overlay',
    cssNamespace: 'custom-autocomplete',
  });

  const playlistInput = document.getElementById('playlist-input');
  playlistInput.classList.add('playlist-search-input');
}

function updateToggleButtonText() {
  const codeDiv = document.querySelector(".code");
  const toggleCodeButton = document.getElementById("toggle-code-button");
  if (codeDiv.style.display === "block") {
    toggleCodeButton.textContent = "Hide generated code";
  } else {
    toggleCodeButton.textContent = "Show generated code";
  }
}

function toggleGeneratedCode() {
  const codeDiv = document.querySelector(".code");
  if (codeDiv.style.display === "block") {
    codeDiv.style.display = "none";
  } else {
    codeDiv.style.display = "block";
  }
  updateToggleButtonText();
}

function initializeToggleCodeButton() {
  const toggleCodeButton = document.getElementById("toggle-code-button");
  toggleCodeButton.addEventListener("click", () => {
    toggleGeneratedCode();
  });
}

function fillQuestion(question) {
  document.querySelector('input[name="question"]').value = question;
}

document.addEventListener("DOMContentLoaded", () => {
  initializeForms();
  initializePlaylistAutocomplete();
  fetchPlaylists();
  initializeToggleCodeButton();
});
