let console_ = console;
const toast_container = document.querySelector('#toast-container');

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

function showAlert(msg, klass = "info") {
    new bootstrap.Alert(alert);
    alert.innerHTML = msg;
    alert.classList = "alert alert-fixed fade in alert-" + klass;
    setTimeout(function () {
        alert.classList.remove("in");
    }, 5000);
}

function showToast(title, content, type = "primary", icon = "") {
    if (icon != null) {
        //icon = `<img class="rounded me-2" src="${icon}" />`;
    }
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