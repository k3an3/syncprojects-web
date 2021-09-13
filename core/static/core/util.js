// noinspection JSUnusedGlobalSymbols
let console_ = console;
// noinspection JSUnusedGlobalSymbols
const toast_container = document.querySelector('#toast-container');
const changes_modal = document.querySelector('#changes_modal');
const proj_re = /projects\/(?<project>[0-9]+)\/(songs\/(?<song>[0-9]+)\/)?/;
const username = document.querySelector('#username').textContent;
const userid = document.querySelector('#userid').textContent;
let playerActive = false;
const context = getContext();

function getContext() {
    let matches = window.location.pathname.match(proj_re);
    if (matches == null)
        return {'project': null, 'song': null};
    return {'project': parseInt(matches.groups.project), 'song': parseInt(matches.groups.song) || null};
}

if (changes_modal != null) {
    let modal = new bootstrap.Modal(changes_modal, {});
    modal.show();
}

if (!document.location.host.startsWith("localhost"))
    console = new Proxy({}, {
        get(target, name) {
            return function () {
            };
        }
    })

function isMobile() {
    const toMatch = [
        /Android/i,
        /webOS/i,
        /iPhone/i,
        /iPad/i,
        /iPod/i,
        /BlackBerry/i,
        /Windows Phone/i,
    ];

    return toMatch.some((toMatchItem) => {
        return navigator.userAgent.match(toMatchItem);
    });
}


// noinspection JSUnusedGlobalSymbols
function showAlert(msg, klass = "info") {
    new bootstrap.Alert(alert_div);
    alert.innerHTML = msg;
    alert.classList = "alert alert-fixed fade in alert-" + klass;
    setTimeout(function () {
        alert.classList.remove("in");
    }, 5000);
}

function showToast(title, content, type = "primary", icon = "") {
    new BsToast({
        title: title,
        subtitle: 'now',
        content: content,
        type: type,
        pause_on_hover: true,
        delay: 5000,
        position: 'top-right',
        img: {src: icon},
        icon: null,
    });
}

function secondsToMMSS(seconds) {
    return String(Math.floor(seconds / 60)).padStart(2, '0') + ":" + String(Math.round(seconds) % 60).padStart(2, '0');

}

function showTime() {
    let cur_time = wavesurfer.getCurrentTime();
    let time = secondsToMMSS(cur_time);
    document.getElementById("MyClockDisplay").innerText = time;
    document.getElementById("MyClockDisplay").textContent = time;
}

let sync_disable = document.querySelector('#sync-disable');
if (sync_disable != null) {
    if (window.localStorage.getItem('sync-disabled') == 1) {
        sync_disable.innerHTML = "Enable sync";
    }
    sync_disable.addEventListener('click', e => {
        let current = window.localStorage.getItem('sync-disabled');
        let result = current == '1' ? '0' : '1';
        console.debug(`Setting sync to ${result} for this browser.`)
        window.localStorage.setItem('sync-disabled', result);
        if (result == '1') {
            sync_disable.innerHTML = "Enable sync";
        } else {
            sync_disable.innerHTML = "Disable sync for browser";
        }
    });
}

function pad(n, width = 2, z = "0") {
    z = z || '0';
    n = n + '';
    return n.length >= width ? n : new Array(width - n.length + 1).join(z) + n;
}

let clicked = false;

function handleCommentTimeClick() {
    clicked = !clicked;
    const time_btn = document.querySelector('#time-button');
    if (clicked) {
        document.querySelector('#time-button').setAttribute('class', 'btn btn-secondary');
        document.querySelector('#song_time').value = wavesurfer.getCurrentTime();
        time_btn.innerHTML += " <span class=\"fas fa-lock\"></span>";
    } else {
        document.querySelector('#time-button').setAttribute('class', 'btn btn-primary');
        document.querySelector('#song_time').value = 0;
        let time = wavesurfer.getCurrentTime();
        time_btn.innerHTML = `Comment at ${pad(Math.floor(time / 60))}:${pad(Math.round(time % 60))} `;
    }
}

function updateClocks() {
    showTime();
    const time_btn = document.querySelector('#time-button');
    if (!clicked) {
        let time = wavesurfer.getCurrentTime();
        time_btn.innerHTML = `Comment at ${pad(Math.floor(time / 60))}:${pad(Math.round(time % 60))} `;
    }
}

let retries = 3;
function setUpPlayer() {
    let time_btn = document.querySelector('#time-button');
    if (time_btn != null)
        time_btn.addEventListener('click', handleCommentTimeClick);
    if (typeof wavesurfer !== 'undefined') {
        showTime();
        if (typeof comment_div !== 'undefined' && comment_div != null) {
            setInterval(updateClocks, 500);
        }
        playerActive = true;
    } else {
        if (retries-- > 0) {
            setTimeout(setUpPlayer, 1000);
        }
        console.log("No player loaded.");
    }
}

function bindEventToSelector(querySelector, func, event = 'click') {
    console.debug("Binding elements with selector " + querySelector);
    let items = document.querySelectorAll(querySelector);
    items.forEach(el => el.addEventListener(event, func));
}

setTimeout(setUpPlayer, 1000);

function fadeIn(elem, ms = 500) {
    if (!elem)
        return;

    elem.style.opacity = 0;
    elem.style.filter = "alpha(opacity=0)";
    elem.style.display = "inline-block";
    elem.style.visibility = "visible";
    elem.removeAttribute('hidden');

    if (ms) {
        let opacity = 0;
        let timer = setInterval(function () {
            opacity += 50 / ms;
            if (opacity >= 1) {
                clearInterval(timer);
                opacity = 1;
            }
            elem.style.opacity = opacity;
            elem.style.filter = "alpha(opacity=" + opacity * 100 + ")";
        }, 50);
    } else {
        elem.style.opacity = 1;
        elem.style.filter = "alpha(opacity=1)";
    }
}

function fadeOut(elem, ms = 500) {
    if (!elem)
        return;

    if (ms) {
        let opacity = 1;
        let timer = setInterval(function () {
            opacity -= 50 / ms;
            if (opacity <= 0) {
                clearInterval(timer);
                opacity = 0;
                elem.style.display = "none";
                elem.style.visibility = "hidden";
            }
            elem.style.opacity = opacity;
            elem.style.filter = "alpha(opacity=" + opacity * 100 + ")";
        }, 50);
    } else {
        elem.style.opacity = 0;
        elem.style.filter = "alpha(opacity=0)";
        elem.style.display = "none";
        elem.style.visibility = "hidden";
    }
}

function show(elem) {
    elem.removeAttribute('hidden');
}

function hide(elem) {
    elem.setAttribute('hidden', 'hidden');
}
