const songUrl = document.getElementById('song_url').innerText;
const waveformDiv = document.getElementById('waveform');
const playerControls = document.getElementById('player-controls');
const playerVolume = document.getElementById('player-volume');
const volInc = 0.1;
const seekInc = 1;
const volMax = 1;
const volMin = 0;

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

wavesurfer.on('ready', function () {
// code that runs after wavesurfer is ready
    console.log('Wavesurfer loaded.');
    fadeOut(document.getElementById('audio-spinner'));
    fadeIn(playerControls);
});

// noinspection JSUnresolvedVariable
wavesurfer.load(songUrl);

function updateVolume(vol) {
    playerVolume.innerText = Math.round(vol * 100).toString() + "%";
}

async function playerControl(e) {
    const action = e.currentTarget.id.split("-")[1];
    console.log("Wavesurfer action " + action);
    let vol = 0;

    switch (action) {
        case "play":
            wavesurfer.playPause();
            if (wavesurfer.isPlaying()) {
                e.target.innerHTML = '<span class="fas fa-pause"></span>';
                e.target.className = "btn btn-warning";
            } else {
                e.target.innerHTML = '<span class="fas fa-play"></span>';
                e.target.className = "btn btn-success";
            }
            break;
        case "forward":
            wavesurfer.skipForward(seekInc);
            break;
        case "backward":
            wavesurfer.skipBackward(seekInc);
            break;
        case "begin":
            wavesurfer.seekTo(0);
            break;
        case "end":
            wavesurfer.seekTo(1);
            break;
        case "loop":

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
            wavesurfer.setMute(!wavesurfer.getMute());
            if (wavesurfer.getMute()) {
                e.target.className = "btn btn-danger";
            } else {
                e.target.className = "btn btn-outline-danger";
            }
            break;
    }
}

wavesurfer.on('pause', () => {
});

wavesurfer.on('play', () => {
});

wavesurfer.on('error', (e) => {
    showToast("Audio Player", "Error: " + e, "danger");
});

bindEventToSelector('.player-control', playerControl);