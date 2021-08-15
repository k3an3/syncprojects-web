const songUrl = document.getElementById('song_url').innerText;
let wavesurfer = WaveSurfer.create({
    container: '#waveform',
    waveColor: 'cyan',
    progressColor: 'blue'
});

wavesurfer.on('ready', function () {
// code that runs after wavesurfer is ready
    console.log('Success');
});

// noinspection JSUnresolvedVariable
wavesurfer.load(songUrl);