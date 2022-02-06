const url =
    'ws://'
    + window.location.host
    + '/ws/notify/';
let notifySocket = new ReconnectingWebSocket(url);

notifySocket.onmessage = e => {
    const data = JSON.parse(e.data);
    showToast(data.title, data.content, data.type, data.icon, 10000);
};

notifySocket.onclose = e => {
    console.error('Notification socket closed unexpectedly');
    showToast("WebSocket Status", "You are disconnected", "danger");
};