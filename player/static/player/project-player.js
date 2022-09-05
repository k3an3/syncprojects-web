let initial = true;
let playing = false;

document.addEventListener('DOMContentLoaded', () => {
    const wavesurfer = WaveSurfer.create({
        container: '#waveform',
        waveColor: 'cyan',
        progressColor: 'blue',
        hideScrollbar: true,
        barWidth: 3,
    });

    const playPause = document.querySelector('#play-pause');
    playPause.addEventListener('click', function () {
        wavesurfer.playPause();
        playing = !playing;
    });

    // Toggle play/pause text
    wavesurfer.on('play', () => {
        if (initial) {
            links[currentTrack].classList.add('active');
            initial = false;
        }
        playing = true;
        document.querySelector('#play').style.display = 'none';
        document.querySelector('#pause').style.display = '';
    });
    wavesurfer.on('pause', () => {
        if (!wavesurfer.isPlaying()) {
            document.querySelector('#play').style.display = '';
            document.querySelector('#pause').style.display = 'none';
        }
    });

    // The playlist links
    const links = document.querySelectorAll('#playlist a');
    let currentTrack = 0;

    // Load a track by index and highlight the corresponding link
    const setCurrentSong = index => {
        links[currentTrack].classList.remove('active');
        if (initial || currentTrack !== index) {
            currentTrack = index;
            wavesurfer.load(links[currentTrack].href);
        }
        if (!initial) {
            links[currentTrack].classList.add('active');
        }
    };

    // Load the track on click
    Array.prototype.forEach.call(links, function (link, index) {
        link.addEventListener('click', function (e) {
            e.preventDefault();
            setCurrentSong(index);
            wavesurfer.play();
        });
    });

    wavesurfer.on('ready', function (e) {
        if (playing) {
            wavesurfer.play();
        }
    });

    wavesurfer.on('error', function (e) {
        console.warn(e);
    });

    // Go to the next track on finish
    wavesurfer.on('finish', function () {
        let newTrack = currentTrack;
        if (currentTrack < links.length - 1) {
            ++newTrack;
            setCurrentSong(newTrack);
        } else {
            initial = true;
            setCurrentSong(0);
            playing = false;
        }
    });

    const next = document.querySelector("#next")
    next.addEventListener('click', function () {
        wavesurfer.cancelAjax();
        let newTrack = currentTrack;
        if (currentTrack < links.length - 1) {
            ++newTrack;
        }
        setCurrentSong(newTrack);
    });

    const prev = document.querySelector("#prev")
    prev.addEventListener('click', function () {
        wavesurfer.cancelAjax();
        let newTrack = currentTrack;
        if (currentTrack > 0) {
            --newTrack;
        }
        setCurrentSong(newTrack);
    });

    // Load the first track
    setCurrentSong(currentTrack);
});