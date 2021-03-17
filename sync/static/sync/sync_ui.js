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
    let result = {'project': parseInt(matches.groups.project), 'song': parseInt(matches.groups.song) || null};
    return result;
}

function showAlert(msg, klass = "info") {
    let this_alert = new bootstrap.Alert(alert);
    alert.innerHTML = msg;
    alert.classList = "alert alert-fixed fade in alert-" + klass;
    setTimeout(function () {
        alert.classList.remove("in");
    }, 5000);
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

if (daw_button != null)
    daw_button.addEventListener('click', async event => {
        daw_button.textContent = "Opening..."
        sync_button.disabled = true;
        let context = getContext();
        console.log("Got context");
        console.log(context);
        let result = null;
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
        if (result.result == "started") {
            pushTask(result.task_id, 'workon');
            showAlert("Syncing and opening song in DAW...");
        } else {
            console.warn("Unknown response.");
        }
    });

sync_button.addEventListener('click', async event => {
    sync_button.textContent = "Syncing..."
    sync_button.disabled = true;
    let context = getContext();
    console.log("Got context");
    console.log(context);
    let result = null;
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
    if (result.result == "started") {
        showAlert("Syncing...");
        pushTask(result.task_id, 'sync');
    } else {
        console.warn("Unknown response.");
    }
});

function disableDawButton(status = true) {
    if (daw_button != null)
        daw_button.disabled = status;
}

async function checkConnection() {
    const result = await ping().catch((error) => {
        ping_failed = true;
        console.error("Failed to connect to syncprojects client: " + error);
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
            sync_button.className = "btn btn-sm btn-primary";
            sync_button.textContent = "Sync";
            sync_button.disabled = false;
            disableDawButton(false);
        }
    }
}

function syncResultHandler(data) {
    sync_modal.show();
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
        switch (result.status) {
            case "progress":
                let task = popTask(result.task_id);
                switch (task) {
                    case 'sync':
                        syncResultHandler(result);
                        break;
                    default:
                        console.warn("Unexpected task handler " + task);
                        break;
                }
                break;
            default:
                console.warn("Unhandled task status " + result.status);
                break;
        }
    });
}

async function checkTasks(force_check = false) {
    if ((!ping_failed || force_check) && taskStore.getObj('tasks') != null && !taskStore.getObj('tasks').isEmpty()) {
        handleResults(await getResults());
    }
}

// noinspection JSIgnoredPromiseFromCall
checkConnection();
// noinspection JSIgnoredPromiseFromCall
checkTasks(true);
setInterval(checkConnection, 15000);
setInterval(checkTasks, 1000);
