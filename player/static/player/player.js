const songUrl = document.getElementById('song_url').innerText;
const waveformDiv = document.getElementById('waveform');
const playerControls = document.getElementById('player-controls');

let wavesurfer = WaveSurfer.create({
    container: '#waveform',
    waveColor: 'cyan',
    progressColor: 'blue',
    hideScrollbar: true,
});

wavesurfer.on('ready', function () {
// code that runs after wavesurfer is ready
    console.log('Wavesurfer loaded.');
    fadeOut(document.getElementById('audio-spinner'));
    fadeIn(playerControls);
});

// noinspection JSUnresolvedVariable
wavesurfer.load(songUrl);

async function playerControl(e) {
    const action = e.currentTarget.id.split("-")[1];
    console.log("Wavesurfer action " + action);

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
            wavesurfer.skipForward(1);
            break;
        case "backward":
            wavesurfer.skipBackward(1);
            break;

    }
}

wavesurfer.on('pause', () => {
});

wavesurfer.on('play', () => {
});


bindEventToSelector('.player-control', playerControl);