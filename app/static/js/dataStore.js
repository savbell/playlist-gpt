export class GptResponse {
    constructor(timestamp, playlistInfo, question, response, code, comments, result, error) {
        this.timestamp = timestamp;
        this.playlistInfo = playlistInfo;
        this.question = question;
        this.response = response;
        this.code = code;
        this.comments = comments;
        this.result = result;
        this.error = error;
    }
}


const eventSystem = {
    events: {},
    subscribe: function (eventName, callback) {
        if (!this.events[eventName]) {
            this.events[eventName] = [];
        }
        this.events[eventName].push(callback);

        return () => {
            this.events[eventName] = this.events[eventName].filter((subscriber) => subscriber !== callback);
        };
    },
    emit: function (eventName, data) {
        if (this.events[eventName]) {
            this.events[eventName].forEach((callback) => callback(data));
        }
    },
    getSubscriber: function (eventName, callback) {
        if (this.events[eventName]) {
            return this.events[eventName].find((subscriber) => subscriber === callback);
        }
        return null;
    },
};


const dataStore = {
    _data: {
        userPlaylists: null,
        playlistName: null,
        playlistId: null,
        playlistInfo: null,
        question: null,
        gptResponses: [],
    },
    get: function (key) {
        return this._data[key];
    },
    set: function (key, value) {
        this._data[key] = value;
        eventSystem.emit(key, value);
    },
    getAllData: function () {
        return { ...this._data };
    },
    updateData: function (updated_data_store) {
        Object.keys(updated_data_store).forEach((key) => {
            this.set(key, updated_data_store[key]);
        });
    },
};


function filterPlaylists(input) {
    const userPlaylists = dataStore.get('userPlaylists');
    return userPlaylists.filter((playlist) => playlist.name.toLowerCase().startsWith(input.toLowerCase()));
};


export { dataStore, eventSystem, filterPlaylists };
