let initial = true;

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
    });

    // Toggle play/pause text
    wavesurfer.on('play', () => {
        if (initial) {
            links[currentTrack].classList.add('active');
            initial = false;
        }
        document.querySelector('#play').style.display = 'none';
        document.querySelector('#pause').style.display = '';
    });
    wavesurfer.on('pause', () => {
        document.querySelector('#play').style.display = '';
        document.querySelector('#pause').style.display = 'none';
    });

    // The playlist links
    const links = document.querySelectorAll('#playlist a');
    let currentTrack = 0;

    // Load a track by index and highlight the corresponding link
    const setCurrentSong = index => {
        links[currentTrack].classList.remove('active');
        currentTrack = index;
        wavesurfer.load(links[currentTrack].href);
        if (!initial) {
            links[currentTrack].classList.add('active');
        }
    };

    // Load the track on click
    Array.prototype.forEach.call(links, function (link, index) {
        link.addEventListener('click', function (e) {
            e.preventDefault();
            setCurrentSong(index);
        });
    });

    wavesurfer.on('error', function (e) {
        console.warn(e);
    });

    // Go to the next track on finish
    wavesurfer.on('finish', function () {
        setCurrentSong((currentTrack + 1) % links.length);
    });

    const next = document.querySelector("#next")
    next.addEventListener('click', function () {
        let newTrack = currentTrack;
        if (currentTrack < links.length - 1) {
            ++newTrack;
        }
        setCurrentSong(newTrack);
        if (wavesurfer.isPlaying()) {
            wavesurfer.play();
        }
    });

    const prev = document.querySelector("#prev")
    prev.addEventListener('click', function () {
        let newTrack = currentTrack;
        if (currentTrack > 0) {
            --newTrack;
        }
        setCurrentSong(newTrack);
        wavesurfer.play();
    });

    // Load the first track
    setCurrentSong(currentTrack);
});