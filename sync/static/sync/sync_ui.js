const proj_re = /projects\/(?<project>[0-9]+)\/(songs\/(?<song>[0-9]+)\/)?/;
const sync_button = document.querySelector('#sync_button');
const daw_button = document.querySelector('#daw_button');
const sync_modal = new bootstrap.Modal(document.querySelector("#sync_modal"), {});
const progress = document.querySelector("#sync_progress");
const alert = document.querySelector('#alert');
let sync_in_progress = false;
let ping_failed = true;

function getContext() {
    let matches = window.location.pathname.match(proj_re);
    if (matches == null)
        return {'project': null, 'song': null};
    return {'project': parseInt(matches.groups.project), 'song': parseInt(matches.groups.song) || null};
}


function pushTask(task_id, data) {
    let tasks = taskStore.getObj('tasks');
    if (tasks == null) {
        tasks = {}
    }
    tasks[task_id] = data;
    taskStore.setObj('tasks', tasks);
}

function clearTasks() {
    taskStore.setObj('tasks', {});
}

function popTask(task_id) {
    let tasks = taskStore.getObj('tasks');
    let result = tasks[task_id];
    delete tasks[task_id];
    taskStore.setObj('tasks', tasks);
    return result;
}

function getTask(task_id) {
    return taskStore.getObj('tasks')[task_id];
}

if (daw_button != null)
    daw_button.addEventListener('click', async _ => {
        daw_button.textContent = "Opening..."
        sync_button.disabled = true;
        let context = getContext();
        console.log("Got context");
        console.log(context);
        let result;
        sync_in_progress = true;
        let msg = {'song': {'song': context.song, 'project': context.project}};
        console.log("Working on song")
        console.log(msg);
        let signed = await signData(msg);
        console.log("Signed data");
        console.log(signed);
        result = await workOn(signed);
        console.log("Got initial response");
        console.log(result);
        if (result.result === "started") {
            pushTask(result.task_id, 'workon');
            showToast("Sync", "Syncing and opening song in DAW...");
        } else {
            console.warn("Unknown response.");
        }
    });

sync_button.addEventListener('click', async _ => {
    showToast("Sync", "Starting sync...");
    sync_button.textContent = "Syncing..."
    sync_button.disabled = true;
    let context = getContext();
    console.log("Got context");
    console.log(context);
    let result;
    sync_in_progress = true;
    if (context.project == null) {
        // Sync all projects
        let projects = await getProjects();
        let msg = {'projects': projects}
        console.log("Syncing projects");
        console.log(msg);
        let signed = await signData(msg);
        console.log("Signed data");
        console.log(signed);
        result = await startSync(signed);
    } else if (context.song == null) {
        // Sync single project
        let msg = {'projects': [context.project]};
        console.log("Syncing project");
        console.log(msg);
        let signed = await signData(msg);
        console.log("Signed data");
        console.log(signed);
        result = await startSync(signed);
    } else {
        // Sync single song
        let msg = {'songs': [{'song': context.song, 'project': context.project}]};
        console.log("Syncing song")
        console.log(msg);
        let signed = await signData(msg);
        console.log("Signed data");
        console.log(signed);
        result = await startSync(signed);
    }
    console.log("Got initial response");
    console.log(result);
    if (result.result === "started") {
        showToast("Sync", "Sync started");
        pushTask(result.task_id, 'sync');
    } else {
        showToast("Sync", "Something went wrong! Contact support.", "danger");
        console.warn("Unknown response.");
    }
});

function disableDawButton(status = true) {
    if (daw_button != null)
        daw_button.disabled = status;
}

function enableSyncButton() {
    sync_button.className = "btn btn-sm btn-primary";
    sync_button.textContent = "Sync";
    sync_button.disabled = false;
    disableDawButton(false);
}

async function checkConnection() {
    const result = await ping().catch(_ => {
        ping_failed = true;
        //console.error("Failed to connect to syncprojects client: " + error);
        sync_button.disabled = true;
        disableDawButton();
        sync_button.className = "btn btn-sm btn-outline-danger";
        sync_button.textContent = "Sync: Not Connected";
    });
    if (result != null && result.result == "pong") {
        ping_failed = false;
        console.debug("Got PONG from server: " + result.task_id);
        if (sync_in_progress) {
            sync_button.className = "btn btn-sm btn-primary";
            sync_button.textContent = "Syncing...";
            sync_button.disabled = true;
            disableDawButton();
        } else {
            enableSyncButton();
        }
    }
}

function syncResultHandler(data) {
    console.log(data);
    sync_modal.show();
}

function saveSyncProgress(data) {
    console.log("Ok... saving progress...");
    console.log(data);
    let stored = taskStore.getObj('sync-' + data.task_id);
    if (stored == null || stored.isEmpty()) {
        console.log("data item doesn't exist in storage");
        stored = [];
        console.log(stored);
    }
    console.log(stored);
    stored.push(data.completed);
    taskStore.setObj('sync-' + data.task_id);
}

function handleResults(data) {
    if (!data.results.length) {
        return;
    }
    console.log("Got results");
    console.log(data.results);
    data.results.forEach(result => {
        console.log("processing");
        console.log(result);
        let task = getTask(result.task_id);
        if (task == null)
            return;
        console.log("Got task");
        console.log(task);
        switch (result.status) {
            case "complete":
                showToast("Sync", task[0].toUpperCase() + task.substr(1) + " complete", "success");
                popTask(result.task_id);
                enableSyncButton();
                switch (task) {
                    case 'sync':
                        syncResultHandler(result);
                        break;
                    default:
                        console.warn("Unexpected task handler " + task);
                        break;
                }
                break;
            case "progress":
                saveSyncProgress(result);
                break;
            case "error":
                task = popTask(result.task_id);
                showToast("Sync", "Oops! " + result.msg, "danger");
                break;
            case "warn":
                showToast("Sync", "Note: " + result.msg, "warning");
                break;
            default:
                console.warn("Unhandled task status " + result.status);
                break;
        }
    });
}

async function checkTasks(force_check = false) {
    if (!isMobile() && (!ping_failed || force_check) && taskStore.getObj('tasks') != null && !taskStore.getObj('tasks').isEmpty()) {
        let results = await getResults().catch(_ => {
        });
        if (results != null)
            handleResults(results);
    }
}

// noinspection JSIgnoredPromiseFromCall
if (!isMobile()) {
    if (daw_button != null)
        daw_button.removeAttribute('hidden');
    sync_button.removeAttribute('hidden');
    checkConnection();
    setInterval(checkConnection, 15000);
}
// noinspection JSIgnoredPromiseFromCall
checkTasks(true);
setInterval(checkTasks, 3000);
