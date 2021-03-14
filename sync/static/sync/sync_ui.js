const proj_re = /projects\/(?<project>[0-9]+)\/(songs\/(?<song>[0-9]+)\/)?/;
const sync_button = document.querySelector('#sync_button');
let sync_in_progress = false;
let ping_failed = true;

function getContext() {
    let matches = window.location.pathname.match(proj_re);
    if (matches == null)
        return {'project': null, 'song': null};
    let result = {'project': parseInt(matches.groups.project), 'song': parseInt(matches.groups.song) || null};
    return result;
}

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
    console.log("Got result");
    console.log(result);
    let tasks = taskStore.getObj('tasks');
    if (tasks == null)
        tasks = [result.task_id];
    else
        tasks.push(result.task_id);
    taskStore.setObj('tasks', tasks);
});

async function checkConnection() {
    const result = await ping().catch((error) => {
        ping_failed = true;
        console.error("Failed to connect to syncprojects client: " + error);
        sync_button.disabled = true;
        sync_button.className = "btn btn-sm btn-outline-danger";
        sync_button.textContent = "Sync: Not Connected";
    });
    if (result != null && result.result == "pong") {
        ping_failed = false;
        console.log("Got PONG from server: " + result.task_id);
        if (sync_in_progress) {
            sync_button.className = "btn btn-sm btn-primary";
            sync_button.textContent = "Syncing...";
            sync_button.disabled = true;
        } else {
            sync_button.className = "btn btn-sm btn-primary";
            sync_button.textContent = "Sync";
            sync_button.disabled = false;
        }
    }
}

function handleResults(data) {
    if (!data.length)
        return;
    console.log("Got results");
    console.log(data);
    data.forEach(result => {
        console.log("processing");
        console.log(result);
    });
}

async function checkTasks(force_check = false) {
    if ((!ping_failed || force_check) && taskStore.getObj('tasks') != null)
        handleResults(await getResults());
}

// noinspection JSIgnoredPromiseFromCall
checkConnection();
// noinspection JSIgnoredPromiseFromCall
checkTasks(true);
setInterval(checkConnection, 15000);
setInterval(checkTasks, 3000);
