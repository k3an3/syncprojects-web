const url =
    (location.protocol === 'https:' ? 'wss://' : 'ws://')
    + window.location.host
    + '/ws/party/';
const partySocket = new ReconnectingWebSocket(url);

partySocket.onmessage = e => {
    const data = JSON.parse(e.data);
    const msg = `${data.user} ${data.action}`;
    showToast("Party Session", msg, "info", "", 10000);
    console.log("Party action " + data.action);

    switch (data.action) {
        case "play":
            wavesurfer.play();
            playButton.innerHTML = '<span class="fas fa-pause"></span>';
            playButton.className = "btn btn-warning player-control";
            break;
        case "pause":
            wavesurfer.pause();
            playButton.innerHTML = '<span class="fas fa-play"></span>';
            playButton.className = "btn btn-success player-control";
            break;
        case "seek":
            wavesurfer.seekTo(data.offset);
            break;
        default:
            console.error("Unhandled action");
            break;
    }
};