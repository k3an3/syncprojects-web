const party_url =
    (location.protocol === 'https:' ? 'wss://' : 'ws://')
    + window.location.host
    + '/ws/party/' + context.song + '/';
let partySocket = null;
const partySessionId = Math.random().toString(36).substr(2);

function activateParty() {
    partySocket = new ReconnectingWebSocket(party_url);
    console.log("Party started");
}

function disableParty() {
    partySocket.close();
    partySocket = null;
    console.log("Party ended");
}

function party_action(action, data={}) {
    if (partySocket != null) {
        data.action = action;
        partySocket.send(JSON.stringify(data));
    }
}
activateParty();

partySocket.onmessage = e => {
    const data = JSON.parse(e.data);
    const msg = `${data.user} ${data.action}`;
    showToast("Party Session", msg, "info", "", 10000);
    console.log("Party action " + data.action);

    switch (data.action) {
        case "play":
            wavesurfer.play();
            //playButton.innerHTML = '<span class="fas fa-pause"></span>';
            //playButton.className = "btn btn-warning player-control";
            break;
        case "pause":
            wavesurfer.pause();
            //playButton.innerHTML = '<span class="fas fa-play"></span>';
            //playButton.className = "btn btn-success player-control";
            break;
        case "seek":
            wavesurfer.seekTo(data.offset);
            break;
        default:
            console.error("Unhandled action");
            break;
    }
};