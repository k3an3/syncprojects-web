const regionDefaults = {
    loop: false,
    drag: false,
    resize: false,
}

async function setUpRegions() {
    let regions = await getRegions(context.song);
    if (regions.results != null) {
        for (let region of regions.results) {
            region.color = hex2RGBA(region.color, 0.33);
            region = {
                ...region,
                ...regionDefaults
            }
            console.log(region);
            wavesurfer.addRegion(region);
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
