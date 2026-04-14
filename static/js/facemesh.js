import { FaceMesh } from '@mediapipe/face_mesh';
import { Hands } from '@mediapipe/hands';
import { Camera } from '@mediapipe/camera_utils';

let faceMesh;
let hands;
let camera;

function initMediaPipe(detector) {
    // Initialize FaceMesh
    faceMesh = new FaceMesh({
        locateFile: (file) => {
            return `https://cdn.jsdelivr.net/npm/@mediapipe/face_mesh/${file}`;
        }
    });
    
    faceMesh.setOptions({
        maxNumFaces: 1,
        refineLandmarks: true,
        minDetectionConfidence: 0.5,
        minTrackingConfidence: 0.5
    });
    
    faceMesh.onResults((results) => {
        detector.detectCap(results);
    });
    
    // Initialize Hands
    hands = new Hands({
        locateFile: (file) => {
            return `https://cdn.jsdelivr.net/npm/@mediapipe/hands/${file}`;
        }
    });
    
    hands.setOptions({
        maxNumHands: 2,
        modelComplexity: 1,
        minDetectionConfidence: 0.5,
        minTrackingConfidence: 0.5
    });
    
    hands.onResults((results) => {
        detector.detectGloves(results);
    });
    
    // Start camera
    const video = document.getElementById('webcam');
    const canvasElement = document.getElementById('output-canvas');
    const canvasCtx = canvasElement.getContext('2d');
    
    camera = new Camera(video, {
        onFrame: async () => {
            await faceMesh.send({image: video});
            await hands.send({image: video});
            
            // Surface cleanliness detection on frame
            if (video.readyState === video.HAVE_ENOUGH_DATA) {
                const frame = captureFrame(video);
                detector.detectSurfaceCleanliness(frame);
                
                // Draw on canvas
                canvasCtx.drawImage(video, 0, 0, 640, 480);
            }
        },
        width: 640,
        height: 480
    });
    
    camera.start();
}

function captureFrame(video) {
    const canvas = document.createElement('canvas');
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    return canvas;
}