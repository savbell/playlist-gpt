import { dataStore } from './dataStore.js';


async function fetchUserPlaylists() {
    const response = await fetch("/playlists");
    const playlists = await response.json();
    dataStore.set('userPlaylists', playlists);
};


async function fetchPlaylistInfo(playlistId) {
    const response = await fetch(`/playlist-info/${playlistId}`);
    const playlistInfo = await response.json();
    return playlistInfo;
};


async function searchPlaylistName(playlistName) {
    const response = await fetch(`/search-playlist/${encodeURIComponent(playlistName)}`);
    const searchResult = await response.json();
    return searchResult;
};


async function resolveShortUrl(shortUrl) {
    const response = await fetch(`/resolve-short-url/${encodeURIComponent(shortUrl)}`);
    const resolvedUrl = await response.json();
    console.log(resolvedUrl)
    return resolvedUrl.id;
}


async function sendFormData(url, data) {
    const response = await fetch(url, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
    });

    if (!response.ok) {
        throw new Error(`An error occurred: ${response.statusText}`);
    }

    const contentType = response.headers.get("content-type");
    if (!contentType || !contentType.includes("application/json")) {
        throw new Error(`Unexpected content type: ${contentType}`);
    }

    return await response.json();
};


export { fetchUserPlaylists, fetchPlaylistInfo, searchPlaylistName, resolveShortUrl, sendFormData };
