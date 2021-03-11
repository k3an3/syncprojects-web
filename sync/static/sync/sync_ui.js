const proj_re = /projects\/(?<project>[0-9]+)\/(songs\/(?<song>[0-9]+)\/)?/;
const sync_button = document.querySelector('#sync_button');

function getContext() {
    let matches = window.location.path.match(proj_re);
    console.log({'proj': matches.groups.project, 'song': matches.groups.song});
    return matches;
}

sync_button.addEventListener('click', event => {
    button.textContent = `Click count: ${event.detail}`;
});

