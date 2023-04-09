let playlists = [];

async function fetchPlaylists() {
  const response = await fetch("/playlists");
  playlists = await response.json();
}

function filterPlaylists(input) {
  return playlists.filter((playlist) => playlist.name.toLowerCase().startsWith(input.toLowerCase()));
}

function showSuggestions(filteredPlaylists) {
  const suggestionsContainer = document.getElementById("playlist-suggestions");
  suggestionsContainer.innerHTML = "";
  
  if (filteredPlaylists.length > 0) {
    suggestionsContainer.style.display = "block";
  } else {
    suggestionsContainer.style.display = "none";
  }

  filteredPlaylists.forEach((playlist) => {
    const suggestion = document.createElement("div");
    suggestion.textContent = playlist.name;
    suggestion.classList.add("playlist-suggestion");
    suggestion.setAttribute("role", "option");
    suggestionsContainer.appendChild(suggestion);
  });
}

document.addEventListener("DOMContentLoaded", () => {
  const playlistInput = document.getElementById("playlist-input");
  
  playlistInput.addEventListener("input", () => {
    const input = playlistInput.value;
    if (input) {
      const filteredPlaylists = filterPlaylists(input);
      showSuggestions(filteredPlaylists);
    } else {
      showSuggestions([]);
    }
  });

  playlistInput.addEventListener("focus", () => {
    const input = playlistInput.value;
    if (input) {
      const filteredPlaylists = filterPlaylists(input);
      showSuggestions(filteredPlaylists);
    }
  });

  playlistInput.addEventListener("blur", () => {
    setTimeout(() => {
      showSuggestions([]);
    }, 200);
  });

  const suggestionsContainer = document.getElementById("playlist-suggestions");
  suggestionsContainer.addEventListener("click", (event) => {
    if (event.target.getAttribute("role") === "option") {
      playlistInput.value = event.target.textContent;
      showSuggestions([]);
    }
  });

  fetchPlaylists();
});

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

document.addEventListener('DOMContentLoaded', () => {
  submitForm();
  fetchPlaylists();
});
