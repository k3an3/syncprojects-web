const url =
    location.protocol === 'https:' ? 'wss://' : 'ws://'
    + window.location.host
    + '/ws/notify/';
const notifySocket = new ReconnectingWebSocket(url);
let hasDisconnected = false;

notifySocket.onmessage = e => {
    const data = JSON.parse(e.data);
    playNotificationSound();
    showToast(data.title, data.content, data.type, data.icon, 10000);
};

notifySocket.onclose = _ => {
    console.error('Notification socket closed');
    setTimeout(showToast, 3000, "WebSocket Status", "You are disconnected", "danger");
    hasDisconnected = true;
};

notifySocket.onopen = _ => {
    if (hasDisconnected) { // just don't show on initial connect
        showToast("WebSocket Status", "Reconnected!", "success");
    }
};

const a = new Audio("/static/notifications/swiftly.mp3");

function playNotificationSound() {
    a.play();
}