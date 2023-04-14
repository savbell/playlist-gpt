import { fetchPlaylistInfo, searchPlaylistName } from './api.js';
import { dataStore, eventSystem } from './dataStore.js';
import {
    handlePlaylistNameEvent,
    handlePlaylistInfoEvent,
    handleGptResponseEvent,
    handleResultEvent,
} from './main.js';


eventSystem.subscribe('playlistName', handlePlaylistNameEvent);


eventSystem.subscribe('playlistInfo', handlePlaylistInfoEvent);


eventSystem.subscribe('gptResponse', handleGptResponseEvent);


eventSystem.subscribe('result', handleResultEvent);


eventSystem.subscribe('playlistId', async (playlist_id) => {
    console.log('playlistId', playlist_id)
    if (playlist_id) {
        const playlist_info = await fetchPlaylistInfo(playlist_id);
        dataStore.set('playlistName', playlist_info.name);
        dataStore.set('playlistInfo', playlist_info);
    } else {
        dataStore.set('playlistInfo', null);
    }
});


async function onPlaylistNameConfirm(value) {
    if (value) {
        const selectedPlaylist = dataStore.get('userPlaylists').find((playlist) => playlist.name === value);
        console.log('selectedPlaylist', selectedPlaylist, 'value', value);
        if (selectedPlaylist && selectedPlaylist.id !== dataStore.get('playlistId')) {
            dataStore.set('playlistId', selectedPlaylist.id);
            console.log('1. playlistId', dataStore.get('playlistId'));
        } else if (!selectedPlaylist) {
            const playlist_info = await searchPlaylistName(value);
            if (playlist_info && playlist_info.id !== dataStore.get('playlistId')) {
                dataStore.set('playlistId', playlist_info.id);
                console.log('2. playlistId', dataStore.get('playlistId'));
            } else {
                dataStore.set('playlistId', null);
                console.log('3. playlistId', dataStore.get('playlistId'));
            }
        }

        const playlist_id = dataStore.get('playlistId');
        console.log('playlistId', playlist_id);
        if (playlist_id) {
            const playlist_info = await fetchPlaylistInfo(playlist_id);
            dataStore.set('playlistName', playlist_info.name);
            dataStore.set('playlistInfo', playlist_info);
        } else {
            dataStore.set('playlistInfo', null);
        }
    }
};


async function onPlaylistFormSubmit(playlist_name, question) {
    console.log('onPlaylistFormSubmit');
    await onPlaylistNameConfirm(playlist_name);
    dataStore.set('question', question);
    dataStore.set('gptResponse', null);
};


function updateDataStore(updated_data_store) {
    dataStore.updateData(updated_data_store);
}


export { onPlaylistNameConfirm, onPlaylistFormSubmit, updateDataStore };
