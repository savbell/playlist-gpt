let playlists = [];

async function fetchPlaylists() {
  const response = await fetch("/playlists");
  playlists = await response.json();
}

function filterPlaylists(input) {
  return playlists.filter((playlist) => playlist.name.toLowerCase().startsWith(input.toLowerCase()));
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

document.addEventListener("DOMContentLoaded", () => {
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

  submitForm();
  fetchPlaylists();
});
