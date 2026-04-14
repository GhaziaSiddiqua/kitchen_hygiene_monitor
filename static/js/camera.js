// static/js/camera.js
// Main camera handling logic

class CameraManager {
    constructor() {
        this.video = null;
        this.stream = null;
        this.isRunning = false;
    }
    
    async initialize(videoElementId) {
        this.video = document.getElementById(videoElementId);
        
        try {
            this.stream = await navigator.mediaDevices.getUserMedia({ 
                video: {
                    width: { ideal: 640 },
                    height: { ideal: 480 },
                    facingMode: "user"
                } 
            });
            
            this.video.srcObject = this.stream;
            await this.video.play();
            this.isRunning = true;
            
            console.log("Camera initialized successfully");
            return true;
            
        } catch (error) {
            console.error("Error accessing camera:", error);
            this.showCameraError(error);
            return false;
        }
    }
    
    showCameraError(error) {
        let message = "Unable to access camera. ";
        
        if (error.name === 'NotAllowedError') {
            message += "Please allow camera access in your browser settings.";
        } else if (error.name === 'NotFoundError') {
            message += "No camera found on this device.";
        } else if (error.name === 'NotReadableError') {
            message += "Camera is already in use by another application.";
        } else {
            message += "Please check your camera settings.";
        }
        
        alert(message);
    }
    
    captureFrame() {
        if (!this.video || !this.isRunning) return null;
        
        const canvas = document.createElement('canvas');
        canvas.width = this.video.videoWidth;
        canvas.height = this.video.videoHeight;
        const ctx = canvas.getContext('2d');
        
        if (ctx && this.video.readyState === this.video.HAVE_ENOUGH_DATA) {
            ctx.drawImage(this.video, 0, 0, canvas.width, canvas.height);
            return canvas;
        }
        
        return null;
    }
    
    stop() {
        if (this.stream) {
            this.stream.getTracks().forEach(track => track.stop());
            this.isRunning = false;
        }
    }
}

// Global camera instance
const cameraManager = new CameraManager();