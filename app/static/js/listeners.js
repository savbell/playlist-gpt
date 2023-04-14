import { fetchPlaylistInfo, searchPlaylistName } from './api.js';
import { dataStore, eventSystem } from './dataStore.js';
import {
    handlePlaylistNameEvent,
    handlePlaylistInfoEvent,
    handleGptResponseEvent,
    hideGeneratedCode,
    hideResult,
} from './main.js';


eventSystem.subscribe('playlistName', handlePlaylistNameEvent);


eventSystem.subscribe('playlistInfo', handlePlaylistInfoEvent);


eventSystem.subscribe('gptResponses', handleGptResponseEvent);


eventSystem.subscribe('playlistId', async (playlist_id) => {
    if (playlist_id) {
        const playlist_info = await fetchPlaylistInfo(playlist_id);
        dataStore.set('playlistName', playlist_info.name);
        dataStore.set('playlistInfo', playlist_info);
    } else {
        dataStore.set('playlistInfo', null);
    }
});


async function updatePlaylistInfo(playlistId) {
    if (playlistId) {
        const playlistInfo = await fetchPlaylistInfo(playlistId);
        dataStore.set('playlistName', playlistInfo.name);
        dataStore.set('playlistInfo', playlistInfo);
    } else {
        dataStore.set('playlistInfo', null);
    }
}

async function onPlaylistNameConfirm(value) {
    if (value) {
        const selectedPlaylist = dataStore.get('userPlaylists').find((playlist) => playlist.name === value);
        if (selectedPlaylist && selectedPlaylist.id !== dataStore.get('playlistId')) {
            dataStore.set('playlistId', selectedPlaylist.id);
        } else if (!selectedPlaylist) {
            const playlist_info = await searchPlaylistName(value);
            if (playlist_info && playlist_info.id !== dataStore.get('playlistId')) {
                dataStore.set('playlistId', playlist_info.id);
            } else {
                dataStore.set('playlistId', null);
            }
        }

        const playlistId = dataStore.get('playlistId');
        await updatePlaylistInfo(playlistId);
    }
};


async function onPlaylistFormSubmit(playlist_name, question) {
    await onPlaylistNameConfirm(playlist_name);
    dataStore.set('question', question);
    dataStore.set('gptResponses', null);
    hideGeneratedCode();
    hideResult();
};


function updateDataStore(updated_data_store) {
    dataStore.updateData(updated_data_store);
}


export { onPlaylistNameConfirm, onPlaylistFormSubmit, updateDataStore, updatePlaylistInfo };
