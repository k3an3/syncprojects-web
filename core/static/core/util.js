// noinspection JSUnusedGlobalSymbols
let console_ = console;
// noinspection JSUnusedGlobalSymbols
const toast_container = document.querySelector('#toast-container');
const changes_modal = document.querySelector('#changes_modal');
const comment_div = document.querySelector('#comment-div');
const comment_div_inner = document.querySelector('#comment-div-inner');
const comment_field = document.querySelector('#comment-field');
const comment_form = document.querySelector('#comment-form');
const proj_re = /projects\/(?<project>[0-9]+)\/(songs\/(?<song>[0-9]+)\/)?/;
const username = document.querySelector('#username').textContent;

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

function showTime() {
    let cur_time = awp_player.getCurrentTime();
    let time = String(Math.floor(cur_time / 60)).padStart(2, '0') + ":" + String(Math.round(cur_time) % 60).padStart(2, '0');
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
    if (clicked) {
        document.querySelector('#time-button').setAttribute('class', 'btn btn-secondary');
        document.querySelector('#song_time').value = awp_player.getCurrentTime();
    } else {
        document.querySelector('#time-button').setAttribute('class', 'btn btn-primary');
        document.querySelector('#song_time').value = 0;
    }
}

function updateClocks() {
    showTime();
    if (!clicked) {
        let time = awp_player.getCurrentTime();
        const time_btn = document.querySelector('#time-button');
        time_btn.innerHTML = `Comment at ${pad(Math.floor(time / 60))}:${pad(Math.round(time % 60))}`;
    }
}

function setUpPlayer() {
    let time_btn = document.querySelector('#time-button');
    if (time_btn != null)
        time_btn.addEventListener('click', handleCommentTimeClick);
    if (awp_player != null) {
        showTime();
        if (comment_div != null) {
            setInterval(updateClocks, 500);
        }
    } else {
        console.log("No player loaded.");
    }
}

async function addComment(comment) {
    let content = '<div class="card col-md-8"><div class="card-header">';
    content += username + " — Just now";
    let time = '';
    if (comment.song_time) {
        time = `<a role="button" class="timecode-link" onclick="awp_player.seek(${comment.song_time});"><h5>${comment.song_time}</h5></a>`;
    }
    content += `</div><div class="card-body">${time}<p class="card-text">${comment.text}</p></div>`;
    content += '<div class="card-footer text-muted"><button class="btn btn-link btn-sm text-muted">Edit</button><button class="btn btn-link btn-sm text-muted">Delete</button></div></div>'
    comment_div_inner.innerHTML = content + comment_div_inner.innerHTML;
}


async function commentFormSubmit(event) {
    event.preventDefault();
    let context = getContext();
    let elements = comment_form.elements;
    let data = {
        text: elements.text.value,
        song_time: parseInt(elements.song_time.value),
        project: context.project,
        song: context.song
    };
    await comment(data);
    addComment(data);
}

if (comment_form) {
    comment_form.addEventListener('submit', commentFormSubmit);
}

if (comment_field != null) {
    comment_field.addEventListener('keyup', k => {

    });
}

window.onload = setUpPlayer;