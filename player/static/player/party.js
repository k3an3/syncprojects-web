const party_url =
    (location.protocol === 'https:' ? 'wss://' : 'ws://')
    + window.location.host
    + '/ws/party/' + context.song + '/';
let partySocket = null;
const browserSessionId = Math.random().toString(36).substr(2);

async function activateParty() {
    partySocket = new ReconnectingWebSocket(party_url);
    registerSocket();
    console.log("Party started");
}

async function disableParty() {
    partySocket.close();
    partySocket = null;
    console.log("Party ended");
}

function party_action(action, data={}) {
    if (partySocket != null) {
        data.action = action;
        data.session = browserSessionId;
        partySocket.send(JSON.stringify(data));
    }
}

function registerSocket() {
    partySocket.onmessage = e => {
        const data = JSON.parse(e.data);
        if (data.session === browserSessionId) {
            return;
        }
        let msg = `${data.user} hit ${data.action}`;
        console.log("Party " + e.data);

        switch (data.action) {
            case "play":
                wavesurfer.play(data.offset);
                if (data.offset !== 0.0) {
                    msg += ` at ${Math.round(data.offset)}`;
                }
                //playButton.innerHTML = '<span class="fas fa-pause"></span>';
                //playButton.className = "btn btn-warning player-control";
                break;
            case "pause":
                wavesurfer.pause();
                //playButton.innerHTML = '<span class="fas fa-play"></span>';
                //playButton.className = "btn btn-success player-control";
                break;
            case "seek":
                wavesurfer.seekTo(data.offset / wavesurfer.getDuration());
                msg = "";
                break;
            case "join":
                msg = `${data.user} joined the party`
                break;
            case "quit":
                msg = `${data.user} left the party`
                break;
            default:
                console.error("Unhandled action");
                return;
        }
        if (msg) {
            showToast("Party Session", msg, "info", "", 10000);
        }
    };

    partySocket.onclose = _ => {
        console.error('Party socket closed');
        setTimeout(showToast, 3000, "Party Status", "Disconnected from party", "danger");
    };

    partySocket.onopen = _ => {
        showToast("Party Status", "Connected to party", "success");
    };
}

