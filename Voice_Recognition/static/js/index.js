
// recorder and close buttons
var startRecordingButton = document.getElementById("startRecordingButton");
var closeButton = document.getElementById("closeButton");
// message and door variables
var response = document.getElementById("message");
let image = document.getElementById("display_image");
let spectrogram = document.getElementById("spectrogram");
// graphs variables
let alter1 = document.getElementById("alter1")
let alter2 = document.getElementById("alter2");
let alter3 = document.getElementById("alter3");

const spectral = document.getElementById("spectral");
const spectral_url = "../static/assets/spectral_centroid.jpg";
const radar = document.getElementById("radar");
const radar_url = "../static/assets/radar.jpg";

var leftchannel = [];
var rightchannel = [];
var recorder = null;
var recordingLength = 0;
var volume = null;
var mediaStream = null;
var sampleRate = 48000;
var context = null;
var blob = null;


startRecordingButton.addEventListener("click", function () {
  // Initialize recorder
    navigator.getUserMedia =
    navigator.getUserMedia ||
    navigator.webkitGetUserMedia ||
    navigator.mozGetUserMedia ||
    navigator.msGetUserMedia;
    navigator.getUserMedia(
    {
    audio: true,
    },
    function (e) {
        console.log("user consent");

    // creates the audio context
    window.AudioContext = window.AudioContext || window.webkitAudioContext;
    context = new AudioContext();

    // creates an audio node from the microphone incoming stream
    mediaStream = context.createMediaStreamSource(e);

    // bufferSize: the onaudioprocess event is called when the buffer is full
    var bufferSize = 2048;
    var numberOfInputChannels = 2;
    var numberOfOutputChannels = 2;
    if (context.createScriptProcessor) {
    recorder = context.createScriptProcessor(
        bufferSize,
        numberOfInputChannels,
        numberOfOutputChannels
        );
    } else {
    recorder = context.createJavaScriptNode(
        bufferSize,
        numberOfInputChannels,
        numberOfOutputChannels
    );
    }

    recorder.onaudioprocess = function (e) {
        leftchannel.push(new Float32Array(e.inputBuffer.getChannelData(0)));
        rightchannel.push(new Float32Array(e.inputBuffer.getChannelData(1)));
        recordingLength += bufferSize;
    };

    // connecting the recorder
    mediaStream.connect(recorder);
    recorder.connect(context.destination);
    },
    function (e) {
        console.error(e);
    }
    );

    setTimeout(stopRecording, 3120);
    startRecordingButton.classList.add("btn-disabled");
});

function stopRecording() {
    // stop recording
    recorder.disconnect(context.destination);
    mediaStream.disconnect(recorder);

    // flat the left and right channels down
    // Float32Array[] => Float32Array
    var leftBuffer = flattenArray(leftchannel, recordingLength);
    var rightBuffer = flattenArray(rightchannel, recordingLength);
    // interleave both channels together
    // [left[0],right[0],left[1],right[1],...]
    var interleaved = interleave(leftBuffer, rightBuffer);

    // create the wav file
    var buffer = new ArrayBuffer(44 + interleaved.length * 2);
    var view = new DataView(buffer);

    // RIFF chunk descriptor
    writeUTFBytes(view, 0, "RIFF");
    view.setUint32(4, 44 + interleaved.length * 2, true);
    writeUTFBytes(view, 8, "WAVE");
    // FMT sub-chunk
    writeUTFBytes(view, 12, "fmt ");
    view.setUint32(16, 16, true); // chunkSize
    view.setUint16(20, 1, true); // wFormatTag
    view.setUint16(22, 2, true); // wChannels: stereo (2 channels)
    view.setUint32(24, sampleRate, true); // dwSamplesPerSec
    view.setUint32(28, sampleRate * 4, true); // dwAvgBytesPerSec
    view.setUint16(32, 4, true); // wBlockAlign
    view.setUint16(34, 16, true); // wBitsPerSample
    // data sub-chunk
    writeUTFBytes(view, 36, "data");
    view.setUint32(40, interleaved.length * 2, true);

    // write the PCM samples
    var index = 44;
    var volume = 1;
    for (var i = 0; i < interleaved.length; i++) {
        view.setInt16(index, interleaved[i] * (0x7fff * volume), true);
        index += 2;
    }

    // final blob
    blob = new Blob([view], { type: "audio/wav" });

    saveRecord(blob);    

    startRecordingButton.classList.remove("btn-disabled");
    setTimeout(showGraphs,1500)

    leftchannel = [];
    rightchannel = [];
    recordingLength = 0;
}

function flattenArray(channelBuffer, recordingLength) {
    var result = new Float32Array(recordingLength);
    var offset = 0;
    for (var i = 0; i < channelBuffer.length; i++) {
        var buffer = channelBuffer[i];
        result.set(buffer, offset);
        offset += buffer.length;
    }
    return result;
}

function interleave(leftChannel, rightChannel) {
    var length = leftChannel.length + rightChannel.length;
    var result = new Float32Array(length);

    var inputIndex = 0;

    for (var index = 0; index < length; ) {
        result[index++] = leftChannel[inputIndex];
        result[index++] = rightChannel[inputIndex];
        inputIndex++;
    }
    return result;
}

function writeUTFBytes(view, offset, string) {
    for (var i = 0; i < string.length; i++) {
        view.setUint8(offset + i, string.charCodeAt(i));
    }
}

// send wav file to back-end
let saveRecord = (audioBlob) => {
    let formdata = new FormData();
    formdata.append("AudioFile", audioBlob, "recordedAudio.wav");
    $.ajax({
        type: "POST",
        url: "http://127.0.0.1:5000/saveRecord",
        data: formdata,
        contentType: false,
        cache: false,
        processData: false,
        success: function(res) {
            // update graphs
            spectral.setAttribute("src", `${spectral_url}?r=${new Date().getTime()}`);
            radar.setAttribute("src", `${radar_url}?r=${new Date().getTime()}`);
            
            if (res == "mostafa" || res == "ahmed" || res == "yehia" || res == "aisha"){
                openTheDoor(res);
            }
            else {
                others();
            }
        },
    });
};


// Control door animation
function showGraphs() {
    alter3.classList.remove("alter_text2");
    alter3.classList.add("alter-collapse");
    spectral.classList.remove("alter-collapse");
}

function openTheDoor(name) {
    response.textContent = "Welcome back, " + name + ".";
    response.classList.add("success");
    response.classList.remove("failed");
    image.src = "../static/img/door_opening.gif";
    closeButton.classList.remove("collapse");
    startRecordingButton.classList.add("btn-disabled");
}

// function dontOpen(name) {
//     response.textContent = "Hello, " + name + ". Sorry can't open the door";
//     response.classList.add("failed");
//     response.classList.remove("success");
// }

function others () {
    response.textContent = "Sorry you're not recognised";
    response.classList.add("failed");
    response.classList.remove("success");
}

closeButton.addEventListener("click", function () {
    response.textContent = "Please say the password";
    response.classList.remove("success");
    response.classList.remove("failed");
    image.src = "../static/img/door_closing.gif";
    closeButton.classList.add("collapse");
    startRecordingButton.classList.remove("btn-disabled");
});


// Animation for record button
$(".activate").on("click touch", function (e) {
var self = $(this);
if (!self.hasClass("loading")) {
    self.addClass("loading");
    setTimeout(function () {
    self.addClass("done");
    setTimeout(function () {
        self.removeClass("loading done");
    }, 1200);
    }, 3120);
}
});







// Control door animation

    // image.src = "../static/img/door_opening.gif";
    // image.src = "../static/img/door_closing.gif";

    // startRecordingButton.classList.add("btn-disabled");
    // startRecordingButton.classList.remove("btn-disabled");
    // closeButton.classList.remove("collapse")

    // response.classList.add("success")
    // response.classList.add("failed");


// setInterval(function () {
//     mfcc.setAttribute("src", `${mfcc_url}?r=${new Date().getTime()}`);
//     spectral.setAttribute("src", `${spectral_url}?r=${new Date().getTime()}`);
    
// }, 3000);