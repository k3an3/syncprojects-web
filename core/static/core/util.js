// noinspection JSUnusedGlobalSymbols
let console_ = console;
// noinspection JSUnusedGlobalSymbols
const toast_container = document.querySelector('#toast-container');
const changes_modal = document.querySelector('#changes_modal');

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
    let time = String(Math.round(cur_time / 60)).padStart(2, '0') + ":" + String(Math.round(cur_time) % 60).padStart(2, '0');
    document.getElementById("MyClockDisplay").innerText = time;
    document.getElementById("MyClockDisplay").textContent = time;

    setTimeout(showTime, 1000);

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

/*
if (awp_player != null) {
}
 */