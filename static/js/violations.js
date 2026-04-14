let violationBuffer = [];
let lastViolationTime = {};

class ViolationDetector {
    constructor(employeeId) {
        this.employeeId = employeeId;
        this.violationCooldown = 5000; // 5 seconds cooldown per violation type
    }
    
    async reportViolation(type, severity = 'medium') {
        const now = Date.now();
        const lastTime = lastViolationTime[type] || 0;
        
        // Prevent spam
        if (now - lastTime < this.violationCooldown) {
            return;
        }
        
        lastViolationTime[type] = now;
        
        try {
            const response = await fetch('/api/log-violation', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    employee_id: this.employeeId,
                    type: type,
                    severity: severity
                })
            });
            
            const data = await response.json();
            if (data.success) {
                this.addToViolationList(type, severity);
                this.updateStatusBadge(type, 'violation');
            }
        } catch (error) {
            console.error('Error reporting violation:', error);
        }
    }
    
    addToViolationList(type, severity) {
        const violationList = document.getElementById('violation-list');
        const listItem = document.createElement('li');
        const timestamp = new Date().toLocaleTimeString();
        listItem.innerHTML = `
            <span class="timestamp">${timestamp}</span>
            <span class="violation-type ${severity}">${type}</span>
            <span class="severity">${severity}</span>
        `;
        violationList.insertBefore(listItem, violationList.firstChild);
        
        // Keep only last 10 violations
        while (violationList.children.length > 10) {
            violationList.removeChild(violationList.lastChild);
        }
    }
    
    updateStatusBadge(type, status) {
        const badgeId = type.toLowerCase().replace(' ', '-') + '-status';
        const badge = document.getElementById(badgeId);
        if (badge) {
            if (status === 'violation') {
                badge.className = 'status-badge violation';
                badge.textContent = '❌ Violation Detected';
                setTimeout(() => {
                    if (badge.textContent === '❌ Violation Detected') {
                        badge.className = 'status-badge success';
                        badge.textContent = '✓ Compliant';
                    }
                }, 2000);
            } else if (status === 'compliant') {
                badge.className = 'status-badge success';
                badge.textContent = '✓ Compliant';
            }
        }
    }
    
    detectCap(faceMeshResults) {
        // Check if head is detected and estimate cap presence
        if (!faceMeshResults.multiFaceLandmarks || faceMeshResults.multiFaceLandmarks.length === 0) {
            this.updateStatusBadge('cap', 'no-face');
            return false;
        }
        
        // Get head bounding box and check top area for cap
        const landmarks = faceMeshResults.multiFaceLandmarks[0];
        const topHead = landmarks[10]; // Top of forehead
        
        // Simple cap detection: check if top of head is covered
        // In production, you'd use a trained model
        const capDetected = this.checkCapCoverage(landmarks);
        
        if (!capDetected) {
            this.reportViolation('No Cap', 'high');
            return false;
        }
        
        this.updateStatusBadge('cap', 'compliant');
        return true;
    }
    
    checkCapCoverage(landmarks) {
        // Placeholder logic - in production, implement proper detection
        // For demo, we'll assume 80% compliance rate for testing
        return Math.random() > 0.2;
    }
    
    detectGloves(handResults) {
        if (!handResults.multiHandLandmarks || handResults.multiHandLandmarks.length === 0) {
            this.updateStatusBadge('gloves', 'no-hands');
            return false;
        }
        
        // Check for gloves by analyzing hand color/skin detection
        const glovesDetected = this.checkGlovesOnHands(handResults);
        
        if (!glovesDetected) {
            this.reportViolation('No Gloves', 'high');
            return false;
        }
        
        this.updateStatusBadge('gloves', 'compliant');
        return true;
    }
    
    checkGlovesOnHands(handResults) {
        // Placeholder logic - in production, use color detection or ML model
        return Math.random() > 0.3;
    }
    
    detectSurfaceCleanliness(frame) {
        // Analyze frame for cleanliness (simplified)
        const cleanliness = this.analyzeCleanliness(frame);
        
        if (cleanliness < 0.7) { // Below 70% clean
            this.reportViolation('Surface Cleanliness Issue', 'medium');
            this.updateStatusBadge('surface', 'violation');
            return false;
        }
        
        this.updateStatusBadge('surface', 'compliant');
        return true;
    }
    
    analyzeCleanliness(frame) {
        // Placeholder - in production, use image analysis
        // For demo, return random score between 0 and 1
        return Math.random();
    }
}

// Initialize detector when page loads
let detector;

document.addEventListener('DOMContentLoaded', () => {
    detector = new ViolationDetector(employeeId);
    
    // Initialize MediaPipe
    initMediaPipe(detector);
});