const record = document.querySelector('.record');
const stop = document.querySelector('.stop');
const canvas = document.querySelector('.visualizer');
const modal = new bootstrap.Modal(document.querySelector('#snippet-modal'));

let recording = false;
let audioCtx;
const canvasCtx = canvas.getContext("2d");
let chunks = [];


if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
    console.log('getUserMedia supported.');
    navigator.mediaDevices.getUserMedia(
        // constraints - only audio needed for this app
        {
            audio: true
        })

        // Success callback
        .then(async function (stream) {
            const mediaRecorder = new MediaRecorder(stream);

            visualize(stream);

            record.onclick = async function () {
                if (!recording) {
                    mediaRecorder.start();
                    console.log(mediaRecorder.state);
                    console.log("recorder started");
                    record.style.background = "red";
                    record.style.color = "black";
                    record.innerText = "Stop";
                    recording = true;
                } else {
                    mediaRecorder.stop();
                    console.log(mediaRecorder.state);
                    console.log("recorder stopped");
                    record.style.background = "";
                    record.style.color = "";
                    record.innerText = "Record";
                    recording = false;
                }
            }

            mediaRecorder.onstop = async function (e) {
                console.log("data available after MediaRecorder.stop() called.");

                //modal.show();
                const clipName = prompt('Enter a name for your sound clip:') + ".ogg";
                let snip = await addSnippet({'name': clipName, 'project': context.project});
                console.log(snip);
                const blob = new Blob(chunks, {'type': 'audio/ogg; codecs=opus'});
                showToast("Snippets", "Snippet created successfully!");
                await fetch(snip.upload_url, {
                    method: 'PUT',
                    mode: 'cors',
                    credentials: 'omit',
                    redirect: 'error',
                    body: blob
                }).then(_ => {
                    showToast("Snippets", "Snippet uploaded! Reloading...", "success");
                    setTimeout(window.location.reload.bind(window.location), 2000);
                }).catch(_ => {
                    showToast("Snippets", "Error in snippet upload!", "danger");
                });
            }

            mediaRecorder.ondataavailable = function (e) {
                chunks.push(e.data);
            }

        })

        // Error callback
        .catch(function (err) {
                console.log('The following getUserMedia error occurred: ' + err);
            }
        );
} else {
    console.log('getUserMedia not supported on your browser!');
}

function visualize(stream) {
    if (!audioCtx) {
        audioCtx = new AudioContext();
    }

    const source = audioCtx.createMediaStreamSource(stream);

    const analyser = audioCtx.createAnalyser();
    analyser.fftSize = 2048;
    const bufferLength = analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufferLength);

    source.connect(analyser);
    //analyser.connect(audioCtx.destination);

    draw()

    function draw() {
        const WIDTH = canvas.width
        const HEIGHT = canvas.height;

        requestAnimationFrame(draw);

        analyser.getByteTimeDomainData(dataArray);

        canvasCtx.fillStyle = 'rgb(200, 200, 200)';
        canvasCtx.fillRect(0, 0, WIDTH, HEIGHT);

        canvasCtx.lineWidth = 2;
        canvasCtx.strokeStyle = 'rgb(0, 0, 0)';

        canvasCtx.beginPath();

        let sliceWidth = WIDTH * 1.0 / bufferLength;
        let x = 0;


        for (let i = 0; i < bufferLength; i++) {

            let v = dataArray[i] / 128.0;
            let y = v * HEIGHT / 2;

            if (i === 0) {
                canvasCtx.moveTo(x, y);
            } else {
                canvasCtx.lineTo(x, y);
            }

            x += sliceWidth;
        }

        canvasCtx.lineTo(canvas.width, canvas.height / 2);
        canvasCtx.stroke();

    }
}
