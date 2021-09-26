const regionMenu = document.getElementById('region-controls');
const DEFAULT_ALPHA = 0.33
let currentRegion = null;
let newRegion = null;
let loopEnabled = false;
let editEnabled = false;
const regionDisplay = document.getElementById('region-display');
const loopBtn = document.getElementById('region-loop');
const editBtn = document.getElementById('region-edit');
const regionModal = new bootstrap.Modal(document.getElementById('region-modal'));
let name = "";
let color = "";


async function setUpRegions() {
    let regions = await getRegions(context.song);
    if (regions.results != null) {
        for (let region of regions.results) {
            region.color = hex2RGBA(region.color, DEFAULT_ALPHA);
            let r = wavesurfer.addRegion(region);
            r.loop = false;
            r.drag = false;
            r.resize = false;
            // by default, the name is the range
            //wavesurfer.regions.list[region.id].element.title = region.name;
            r.element.title = region.name;
            allRegions[region.id] = region;
        }
    } else {
        console.log("No regions found for song.");
    }
}

const hex2RGBA = (hex, alpha = 1) => {
    const [r, g, b] = hex.match(/\w\w/g).map(x => parseInt(x, 16));
    return `rgba(${r},${g},${b},${alpha})`;
};

const RGBA2Hex = (rgbaString) => {
    const rgba = rgbaString.replace(/^rgba?\(|\s+|\)$/g, '').split(',');
    return `${((1 << 24) + (parseInt(rgba[0]) << 16) + (parseInt(rgba[1]) << 8) + parseInt(rgba[2])).toString(16).slice(1)}`;
}

function showRegionMenu(region) {
    if (region == currentRegion) {
        return;
    }
    currentRegion = region;
    region = allRegions[region.id];
    console.log(region);
    document.getElementById('region-title').innerText = region.name;
    document.getElementById('region-start').value = secondsToMMSS(region.start);
    document.getElementById('region-end').value = secondsToMMSS(region.end);
    if (loopEnabled) {
        loopBtn.className = "btn btn-warning btn-sm region-control";
    } else {
        loopBtn.className = "btn btn-default btn-sm region-control";
    }
    fadeIn(regionMenu);
}

wavesurfer.on('region-in', (e) => {
    if (allRegions[e.id]) {
        regionDisplay.innerText = allRegions[e.id].name;
    } else {
        regionDisplay.innerText = name;
    }
});

wavesurfer.on('region-out', (e) => {
    regionDisplay.innerText = "";
});

wavesurfer.on('region-click', (e) => {
    if (allRegions[e.id]) {
        regionDisplay.innerText = allRegions[e.id].name;
    } else {
        regionDisplay.innerText = name;
    }
    showRegionMenu(e);
});

wavesurfer.on('region-dblclick', (e) => {
});

wavesurfer.on('region-mouseenter', (e) => {
});

wavesurfer.on('region-mouseleave', (e) => {
});

wavesurfer.on('region-update-end', (e) => {
    document.getElementById('region-save').removeAttribute('disabled');
    currentRegion = e;
    e.play();
});

async function regionControl(e) {
    const action = e.currentTarget.id.split("-")[1];
    console.log("Wavesurfer region action " + action);

    switch (action) {
        case 'play':
            currentRegion.play();
            break;
        case 'loop':
            currentRegion.loop = !loopEnabled;
            if (loopEnabled) {
                loopBtn.className = "btn btn-default btn-sm region-control";
            } else {
                loopBtn.className = "btn btn-warning btn-sm region-control";
            }
            loopEnabled = !loopEnabled;
            break;
        case 'edit':
            if (editEnabled) {
                currentRegion.drag = false;
                currentRegion.resize = false;
                editBtn.className = "btn btn-warning btn-sm region-control";
                editBtn.innerHTML = "Enable Editing <span class=\"fas fa-plus\"></span";
                let r = {
                    ...allRegions[currentRegion.id],
                    color: RGBA2Hex(currentRegion.color),
                    start: currentRegion.start,
                    end: currentRegion.end,
                }
                await addRegion(r, currentRegion.id);
                showToast("Regions", "Region edited successfully", "success");
            } else {
                currentRegion.drag = true;
                currentRegion.resize = true;
                showToast("Regions", "The region can now be resized by clicking the edges and dragging, or moved by clicking anywhere in the region and dragging it to a new location.");
                editBtn.className = "btn btn-success btn-sm region-control";
                editBtn.innerHTML = "Save Edits <span class=\"fas fa-save\"></span>";
            }
            editEnabled = !editEnabled;
            break;
        case 'close':
            fadeOut(regionMenu);
            currentRegion = null;
            break;
        case 'delete':
            currentRegion.remove();
            delete allRegions[currentRegion.id];
            fadeOut(regionMenu);
            showToast("Regions", "Region deleted", "success");
            break;
        case 'add':
            regionModal.show();
            break;
        case 'save':
            // Current region was updated when it was dragged
            document.getElementById('region-save').setAttribute('hidden', 'hidden');
            document.getElementById('region-add').removeAttribute('hidden');
            editEnabled = false;
            let r = {
                color: RGBA2Hex(currentRegion.color),
                start: currentRegion.start,
                end: currentRegion.end,
                name: name,
                color: color.replace('#', ''),
                song: context.song,
            }
            let newRegion = await addRegion(r);
            allRegions[currentRegion.id] = newRegion;
            showToast("Regions", "Region created successfully", "success");
            currentRegion = null;
            break;
        case 'commit':
            let nameField = document.getElementById('region-name');
            name = nameField.value.trim();
            let colorField = document.getElementById('region-color');
            color = colorField.value;
            if (name == null || name.length === 0 || color == null) {
                showToast('Region Editor', 'Region name cannot be blank', 'danger')
                return;
            }
            wavesurfer.enableDragSelection({
                color: hex2RGBA(color, DEFAULT_ALPHA),
            });
            showToast('Region Editor', 'Region created! Select the desired region of the song; click and drag to adjust.', 'success')
            document.getElementById('region-save').removeAttribute('hidden');
            document.getElementById('region-add').setAttribute('hidden', 'hidden');
            document.getElementById('region-save').setAttribute('disabled', 'disabled');
            regionModal.hide();
            nameField.value = "";
            colorField.value = "#ffffff";
            editEnabled = true;
            break;
    }
}

bindEventToSelector(".region-control", regionControl);