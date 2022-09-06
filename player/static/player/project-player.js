let initial = true;
let wavesurfer;
let playing = false;
let links;
let currentTrack = 0;
const partyButton = document.getElementById('party-toggle');
let party = false;

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

// Load a track by index and highlight the corresponding link
function setCurrentSong(index, remote=false) {
    links[currentTrack].classList.remove('active');
    if (!initial && !remote) {
        partyAction("song", {song: index});
    }
    if (initial || currentTrack !== index) {
        currentTrack = index;
        wavesurfer.load(links[currentTrack].href);
    }
    if (!initial) {
        links[currentTrack].classList.add('active');
    }
};

document.addEventListener('DOMContentLoaded', () => {
    wavesurfer = WaveSurfer.create({
        container: '#waveform',
        waveColor: 'cyan',
        progressColor: 'blue',
        hideScrollbar: true,
        barWidth: 3,
    });

    const playPause = document.querySelector('#play-pause');
    playPause.addEventListener('click', function () {
        playing = !playing;
        wavesurfer.playPause();
        if (playing) {
            partyAction("play", {offset: wavesurfer.getCurrentTime()});
        } else {
            partyAction("pause");
        }
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
    links = document.querySelectorAll('#playlist a');

    // Load the track on click
    Array.prototype.forEach.call(links, function (link, index) {
        link.addEventListener('click', function (e) {
            e.preventDefault();
            setCurrentSong(index);
            wavesurfer.play();
            partyAction("play", {offset: wavesurfer.getCurrentTime()});
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

    wavesurfer.on('seek', () => {
        partyAction('seek', {offset: wavesurfer.getCurrentTime()});
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