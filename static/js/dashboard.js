let violationsChart;
let employeeChart;

async function loadDashboardData() {
    try {
        // Load statistics
        const statsResponse = await fetch('/api/get-stats');
        const stats = await statsResponse.json();
        
        document.getElementById('total-violations').textContent = stats.total;
        document.getElementById('today-violations').textContent = stats.today;
        
        // Update violation type counts
        stats.by_type.forEach(type => {
            if (type.type === 'No Cap') {
                document.getElementById('no-cap-count').textContent = type.count;
            } else if (type.type === 'No Gloves') {
                document.getElementById('no-gloves-count').textContent = type.count;
            }
        });
        
        // Update charts
        updateCharts(stats);
        
        // Load violations table
        const violationsResponse = await fetch('/api/get-violations');
        const violations = await violationsResponse.json();
        updateViolationsTable(violations);
        
    } catch (error) {
        console.error('Error loading dashboard data:', error);
    }
}

function updateCharts(stats) {
    // Violations by type chart
    const typeLabels = stats.by_type.map(t => t.type);
    const typeData = stats.by_type.map(t => t.count);
    
    if (violationsChart) {
        violationsChart.destroy();
    }
    
    const ctx = document.getElementById('violations-chart').getContext('2d');
    violationsChart = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: typeLabels,
            datasets: [{
                label: 'Number of Violations',
                data: typeData,
                backgroundColor: ['#ff6b6b', '#4ecdc4', '#45b7d1'],
                borderColor: '#333',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Count'
                    }
                }
            }
        }
    });
    
    // Employee ranking chart
    const employeeNames = stats.employee_ranking.map(e => e.name);
    const employeeCounts = stats.employee_ranking.map(e => e.violation_count);
    
    if (employeeChart) {
        employeeChart.destroy();
    }
    
    const ctx2 = document.getElementById('employee-chart').getContext('2d');
    employeeChart = new Chart(ctx2, {
        type: 'horizontalBar',
        data: {
            labels: employeeNames,
            datasets: [{
                label: 'Violations',
                data: employeeCounts,
                backgroundColor: '#ffa500'
            }]
        },
        options: {
            responsive: true,
            indexAxis: 'y',
            scales: {
                x: {
                    beginAtZero: true,
                    title: {
                        display: true,
                        text: 'Number of Violations'
                    }
                }
            }
        }
    });
}

function updateViolationsTable(violations) {
    const tableBody = document.getElementById('violations-table-body');
    tableBody.innerHTML = '';
    
    violations.forEach(violation => {
        const row = tableBody.insertRow();
        row.innerHTML = `
            <td>${new Date(violation.timestamp).toLocaleString()}</td>
            <td>${violation.employee_name}</td>
            <td>${violation.department || 'N/A'}</td>
            <td class="violation-${violation.type.toLowerCase().replace(' ', '-')}">${violation.type}</td>
            <td><span class="severity-badge ${violation.severity}">${violation.severity}</span></td>
        `;
    });
}

async function exportToPDF() {
    const { jsPDF } = window.jspdf;
    const element = document.querySelector('.dashboard-container');
    
    // Show loading indicator
    const exportBtn = document.querySelector('.export-btn');
    const originalText = exportBtn.textContent;
    exportBtn.textContent = 'Generating PDF...';
    exportBtn.disabled = true;
    
    try {
        const canvas = await html2canvas(element, {
            scale: 2,
            logging: false,
            useCORS: true
        });
        
        const imgData = canvas.toDataURL('image/png');
        const pdf = new jsPDF('p', 'mm', 'a4');
        const imgWidth = 210;
        const imgHeight = (canvas.height * imgWidth) / canvas.width;
        
        pdf.addImage(imgData, 'PNG', 0, 0, imgWidth, imgHeight);
        pdf.save('hygiene-violations-report.pdf');
    } catch (error) {
        console.error('Error generating PDF:', error);
        alert('Error generating PDF. Please try again.');
    } finally {
        exportBtn.textContent = originalText;
        exportBtn.disabled = false;
    }
}

function logout() {
    window.location.href = '/logout';
}

// Auto-refresh every 10 seconds
setInterval(loadDashboardData, 10000);
loadDashboardData();