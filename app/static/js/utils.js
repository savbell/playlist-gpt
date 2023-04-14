function decodeHtmlEntities(str) {
    const textarea = document.createElement('textarea');
    textarea.innerHTML = str;
    return textarea.value;
};


function extractPlaylistIdFromLink(link) {
    const regex = /(?:spotify:playlist:|open\.spotify\.com\/playlist\/|https:\/\/spotify\.link\/)([a-zA-Z0-9]+)/;
    const match = link.match(regex);
    return match ? { id: match[1], isShortUrl: link.startsWith('https://spotify.link') } : null;
}


export { decodeHtmlEntities, extractPlaylistIdFromLink };
