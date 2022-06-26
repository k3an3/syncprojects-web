const songUrlE = document.getElementById('song_url');
let songUrl = "";
if (songUrlE) {
    songUrl = songUrlE.innerText;
}
const waveformDiv = document.getElementById('waveform');
const playerControls = document.getElementById('player-controls');
const playerVolume = document.getElementById('player-volume');
const playButton = document.getElementById('player-play');
const partyButton = document.getElementById('party-toggle');
const volInc = 0.1;
const seekInc = 1;
const volMax = 1;
const volMin = 0;
let loopAll = false;
let party = false;

let wavesurfer = WaveSurfer.create({
    container: '#waveform',
    waveColor: 'cyan',
    progressColor: 'blue',
    hideScrollbar: true,
    plugins: [
        WaveSurfer.regions.create({}),
        WaveSurfer.markers.create({}),
    ]
});

wavesurfer.on('ready', async function () {
// code that runs after wavesurfer is ready
    console.log('Wavesurfer loaded.');
    fadeOut(document.getElementById('audio-spinner'));
    fadeIn(playerControls);
    await Promise.all([setUpMarkers(), setUpRegions()]);
    let vol = localStorage.getItem('player_volume');
    if (vol != null) {
        console.debug("Restoring saved volume to: " + vol);
        wavesurfer.setVolume(parseInt(vol));
    } else {
        vol = 1;
    }
    updateVolume(vol);
});

let allComments = {};
let allRegions = {};

async function setUpMarkers() {
    wavesurfer.clearMarkers();
    if (context.song) {
        let comments = await getComments(null, context.song);
        allComments = {};
        if (comments.results != null) {
            for (const comment of comments.results) {
                if (comment.song_time_seconds && !comment.resolved) {
                    allComments[comment.song_time_seconds] = comment;
                    addMarker(comment.song_time_seconds, comment.requires_resolution ? "yellow" : "blue");
                }
            }
        }
    }
}

// noinspection JSUnresolvedVariable
wavesurfer.load(songUrl);

function updateVolume(vol) {
    localStorage.setItem('player_volume', vol.toString());
    playerVolume.innerText = Math.round(vol * 100).toString() + "%";
}

function addMarker(time, color = "gray", text = "", position = "top") {
    return wavesurfer.addMarker({time: time, label: text, color: color, position: position});
}

async function playerControl(e) {
    const action = e.currentTarget.id.split("-")[1];
    console.log("Wavesurfer action " + action);
    let vol = 0;

    switch (action) {
        case "play":
            wavesurfer.playPause();
            if (wavesurfer.isPlaying()) {
                partyAction('play', {offset: wavesurfer.getCurrentTime()});
                e.currentTarget.innerHTML = '<span class="fas fa-pause"></span>';
                e.currentTarget.className = "btn btn-warning player-control";
            } else {
                partyAction('pause');
                e.currentTarget.innerHTML = '<span class="fas fa-play"></span>';
                e.currentTarget.className = "btn btn-success player-control";
            }
            break;
        case "forward":
            wavesurfer.skipForward(seekInc);
            partyAction('seek', {'offset': wavesurfer.getCurrentTime()});
            break;
        case "backward":
            wavesurfer.skipBackward(seekInc);
            partyAction('seek', {'offset': wavesurfer.getCurrentTime()});
            break;
        case "begin":
            wavesurfer.seekTo(0);
            partyAction('seek', {'offset': 0});
            break;
        case "end":
            wavesurfer.seekTo(1);
            partyAction('seek', {'offset': 1});
            break;
        case "loop":
            loopAll = !loopAll;
            if (loopAll) {
                e.currentTarget.className = "btn btn-warning player-control";
            } else {
                e.currentTarget.className = "btn btn-default player-control";
            }
        case "volup":
            vol = wavesurfer.getVolume();
            if (vol + volInc <= volMax) {
                vol += volInc;
                wavesurfer.setVolume(vol);
                updateVolume(vol);
            } else {
                wavesurfer.setVolume(volMax);
            }
            break;
        case "voldown":
            vol = wavesurfer.getVolume();
            if (vol - volInc >= volMin) {
                vol -= volInc;
                wavesurfer.setVolume(vol);
                updateVolume(vol);
            } else {
                wavesurfer.setVolume(volMin);
            }
            break;
        case "mute":
            let mute = !wavesurfer.getMute();
            wavesurfer.setMute(mute);
            if (mute) {
                e.currentTarget.className = "btn btn-danger player-control";
            } else {
                e.currentTarget.className = "btn btn-outline-danger player-control";
            }
            break;
    }
}

wavesurfer.on('pause', () => {
    playButton.innerHTML = '<span class="fas fa-play"></span>';
    playButton.className = "btn btn-success";
});

wavesurfer.on('play', () => {
    playButton.innerHTML = '<span class="fas fa-pause"></span>';
    playButton.className = "btn btn-warning";
});

wavesurfer.on('marker-click', (e) => {
    window.location = '#comment-' + allComments[e.time].id;
});

wavesurfer.on('seek', () => {
    partyAction('seek', {offset: wavesurfer.getCurrentTime()});
});

wavesurfer.on('error', (e) => {
    showToast("Audio Player", "Error: " + e, "danger");
    document.getElementById("audio-spinner").innerHTML = "<strong>Error loading audio</strong>";
});

wavesurfer.on('finish', (e) => {
    if (loopAll) {
        wavesurfer.playPause();
        partyAction('play', {'offset': 0.0});
        setTimeout(_ => {
            playButton.innerHTML = '<span class="fas fa-pause"></span>';
            playButton.className = "btn btn-warning";
        }, 300);
    }
});

bindEventToSelector('.player-control', playerControl);

partyButton.addEventListener('click', async _ => {
    if (!party) {
        await activateParty();
        partyButton.innerHTML = 'Leave Party Session <span class="fas fa-users"></span>';
        partyButton.className = "btn btn-danger";
    } else {
        await disableParty();
        partyButton.innerHTML = 'Join Party Session <i class="fas fa-users"></i>';
        partyButton.className = "btn btn-secondary";
    }
    party = !party;
});
