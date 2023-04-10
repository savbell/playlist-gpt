let playlists = [];

async function fetchPlaylists() {
  const response = await fetch("/playlists");
  playlists = await response.json();
}

function filterPlaylists(input) {
  return playlists.filter((playlist) => playlist.name.toLowerCase().startsWith(input.toLowerCase()));
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
}

function fillQuestion(question) {
    document.querySelector('input[name="question"]').value = question;
  }

function showLoadingIndicator() {
    const loadingIndicator = document.getElementById('loading-indicator');
    loadingIndicator.style.display = 'block';
  }
  
function submitForm() {
  const form = document.getElementById('playlist-form');
  form.addEventListener('submit', (event) => {
    event.preventDefault();
    showLoadingIndicator();
    form.submit();
  });
}

function submitCodeForm() {
  const codeForm = document.getElementById('code-form');
  if (codeForm) {
    codeForm.addEventListener('submit', (event) => {
      event.preventDefault();
      showLoadingIndicator();
      codeForm.submit();
    });
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

document.addEventListener("DOMContentLoaded", () => {
  initializePlaylistAutocomplete();
  submitForm();
  submitCodeForm();
  fetchPlaylists();
});
