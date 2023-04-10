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

function updateUI(data) {
  const { result, playlist_name, gpt_response } = data;

  if (gpt_response) {
    document.getElementById("generated-response").textContent = gpt_response;
    document.getElementById("hidden-playlist-name").value = playlist_name;
    document.getElementById("hidden-gpt-response").value = gpt_response;
    document.querySelector(".code").style.display = "block";
  }
  if (result) {
    document.getElementById("result-text").innerHTML = result;
    document.querySelector(".result").style.display = "block";
  }
} 

async function sendFormData(url, formData) {
  const response = await fetch(url, {
    method: "POST",
    body: formData,
  });
  return await response.json();
}

async function submitForm(event) {
  event.preventDefault();
  showLoadingIndicator();
  const formData = new FormData(event.target);
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

async function displayPlaylistInfo(playlistId) {
  const response = await fetch(`/playlist-info/${playlistId}`);
  const playlistInfo = await response.json();

  document.getElementById('playlist-name').innerHTML = `<a href="${playlistInfo.external_urls.spotify}" target="_blank">
    ${decodeHtmlEntities(playlistInfo.name)}</a>`;
  document.getElementById('playlist-image').src = playlistInfo.images[0].url || "";
  document.getElementById('playlist-description').textContent = decodeHtmlEntities(playlistInfo.description) 
    || "No description provided.";
  document.getElementById('author-name').textContent = decodeHtmlEntities(playlistInfo.owner.display_name) 
    || "Unavailable";
  document.getElementById('author-name').href = playlistInfo.owner.external_urls.spotify || "#";
  document.getElementById('playlist-info').style.display = 'block';

  if (data.result) {
    displayResult(data);
  }

  if (data.gpt_response) {
    document.querySelector('.code').style.display = 'block';
    document.querySelector('#generated-code').textContent = data.gpt_response;
    document.querySelector('#hidden-playlist-name').value = data.playlist_name;
    document.querySelector('#hidden-gpt-response').value = data.gpt_response;
  } else {
    document.querySelector('.code').style.display = 'none';
  }
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

function fillQuestion(question) {
  document.querySelector('input[name="question"]').value = question;
}

document.addEventListener("DOMContentLoaded", () => {
  initializeForms();
  initializePlaylistAutocomplete();
  fetchPlaylists();
});
 