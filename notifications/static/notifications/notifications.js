const notifySocket = new WebSocket(
    'ws://'
    + window.location.host
    + '/ws/notify/'
);

notifySocket.onmessage = function (e) {
    const data = JSON.parse(e.data);
    showToast(data.title, data.content, data.type, data.icon);
};

notifySocket.onclose = function (e) {
    console.error('Notification socket closed unexpectedly');
};