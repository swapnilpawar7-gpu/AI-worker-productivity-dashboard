/**
 * Worker Productivity Dashboard - Frontend Application
 * =====================================================
 * Vanilla JavaScript application for displaying AI camera event analytics.
 * Fetches computed metrics from the Flask backend and renders them in the UI.
 */

// Configuration
const API_BASE_URL = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
    ? 'http://localhost:5000'
    : '/api'; // For production/Docker setup

// State
let workersData = [];
let workstationsData = [];
let currentFilter = 'all';

// DOM Elements
const elements = {
    // Factory metrics
    totalProductiveHours: document.getElementById('totalProductiveHours'),
    totalIdleHours: document.getElementById('totalIdleHours'),
    totalProduction: document.getElementById('totalProduction'),
    avgProductionRate: document.getElementById('avgProductionRate'),
    avgUtilization: document.getElementById('avgUtilization'),
    activeWorkers: document.getElementById('activeWorkers'),
    factoryComputedAt: document.getElementById('factoryComputedAt'),
    
    // Tables
    workersTableBody: document.getElementById('workersTableBody'),
    workstationsTableBody: document.getElementById('workstationsTableBody'),
    
    // Filter
    filterSelect: document.getElementById('filterSelect'),
    workerOptions: document.getElementById('workerOptions'),
    stationOptions: document.getElementById('stationOptions'),
    
    // Sections
    workersSection: document.getElementById('workersSection'),
    workstationsSection: document.getElementById('workstationsSection'),
    
    // Buttons
    refreshBtn: document.getElementById('refreshBtn'),
    seedBtn: document.getElementById('seedBtn'),
    
    // Status
    statusMessage: document.getElementById('statusMessage'),
    apiUrl: document.getElementById('apiUrl')
};

/**
 * Show a status message to the user
 */
function showStatus(message, type = 'info') {
    elements.statusMessage.textContent = message;
    elements.statusMessage.className = `status-message ${type}`;
    
    // Auto-hide after 3 seconds
    setTimeout(() => {
        elements.statusMessage.classList.add('hidden');
    }, 3000);
}

/**
 * Format a datetime string for display
 */
function formatDateTime(isoString) {
    if (!isoString || isoString === '--') return '--';
    try {
        const date = new Date(isoString);
        return date.toLocaleString();
    } catch {
        return isoString;
    }
}

/**
 * Get utilization badge class based on percentage
 */
function getUtilizationClass(percent) {
    if (percent >= 75) return 'utilization-high';
    if (percent >= 50) return 'utilization-medium';
    return 'utilization-low';
}

/**
 * Fetch factory-level metrics from the API
 */
async function fetchFactoryMetrics() {
    try {
        const response = await fetch(`${API_BASE_URL}/metrics/factory`);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        
        const data = await response.json();
        const metrics = data.metrics;
        
        elements.totalProductiveHours.textContent = metrics.total_productive_hours;
        elements.totalIdleHours.textContent = metrics.total_idle_hours;
        elements.totalProduction.textContent = metrics.total_production_count.toLocaleString();
        elements.avgProductionRate.textContent = metrics.average_production_rate;
        elements.avgUtilization.textContent = metrics.average_worker_utilization;
        elements.activeWorkers.textContent = metrics.active_workers;
        elements.factoryComputedAt.textContent = formatDateTime(data.computed_at);
        
    } catch (error) {
        console.error('Error fetching factory metrics:', error);
        showStatus('Failed to load factory metrics', 'error');
    }
}

/**
 * Fetch worker metrics from the API
 */
async function fetchWorkerMetrics() {
    try {
        const response = await fetch(`${API_BASE_URL}/metrics/workers`);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        
        const data = await response.json();
        workersData = data.metrics;
        
        renderWorkersTable();
        updateWorkerFilterOptions();
        
    } catch (error) {
        console.error('Error fetching worker metrics:', error);
        elements.workersTableBody.innerHTML = '<tr><td colspan="7" class="no-data">Failed to load worker data</td></tr>';
    }
}

/**
 * Fetch workstation metrics from the API
 */
async function fetchWorkstationMetrics() {
    try {
        const response = await fetch(`${API_BASE_URL}/metrics/workstations`);
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        
        const data = await response.json();
        workstationsData = data.metrics;
        
        renderWorkstationsTable();
        updateStationFilterOptions();
        
    } catch (error) {
        console.error('Error fetching workstation metrics:', error);
        elements.workstationsTableBody.innerHTML = '<tr><td colspan="6" class="no-data">Failed to load workstation data</td></tr>';
    }
}

/**
 * Render the workers table
 */
function renderWorkersTable() {
    if (workersData.length === 0) {
        elements.workersTableBody.innerHTML = '<tr><td colspan="7" class="no-data">No worker data available</td></tr>';
        return;
    }
    
    elements.workersTableBody.innerHTML = workersData.map(worker => {
        const utilizationClass = getUtilizationClass(worker.utilization_percent);
        const isHidden = currentFilter !== 'all' && 
                         !currentFilter.startsWith('station-') && 
                         currentFilter !== `worker-${worker.worker_id}`;
        
        return `
            <tr data-worker-id="${worker.worker_id}" class="${isHidden ? 'hidden' : ''}">
                <td><strong>${worker.worker_id}</strong></td>
                <td>${worker.name}</td>
                <td>${worker.active_time_hours}</td>
                <td>${worker.idle_time_hours}</td>
                <td><span class="utilization-badge ${utilizationClass}">${worker.utilization_percent}%</span></td>
                <td>${worker.total_units_produced.toLocaleString()}</td>
                <td>${worker.units_per_hour}</td>
            </tr>
        `;
    }).join('');
}

/**
 * Render the workstations table
 */
function renderWorkstationsTable() {
    if (workstationsData.length === 0) {
        elements.workstationsTableBody.innerHTML = '<tr><td colspan="6" class="no-data">No workstation data available</td></tr>';
        return;
    }
    
    elements.workstationsTableBody.innerHTML = workstationsData.map(station => {
        const utilizationClass = getUtilizationClass(station.utilization_percent);
        const isHidden = currentFilter !== 'all' && 
                         !currentFilter.startsWith('worker-') && 
                         currentFilter !== `station-${station.station_id}`;
        
        return `
            <tr data-station-id="${station.station_id}" class="${isHidden ? 'hidden' : ''}">
                <td><strong>${station.station_id}</strong></td>
                <td>${station.name}</td>
                <td>${station.occupancy_hours}</td>
                <td><span class="utilization-badge ${utilizationClass}">${station.utilization_percent}%</span></td>
                <td>${station.total_units_produced.toLocaleString()}</td>
                <td>${station.throughput_rate}</td>
            </tr>
        `;
    }).join('');
}

/**
 * Update worker filter options
 */
function updateWorkerFilterOptions() {
    elements.workerOptions.innerHTML = workersData.map(worker => 
        `<option value="worker-${worker.worker_id}">${worker.worker_id} - ${worker.name}</option>`
    ).join('');
}

/**
 * Update workstation filter options
 */
function updateStationFilterOptions() {
    elements.stationOptions.innerHTML = workstationsData.map(station => 
        `<option value="station-${station.station_id}">${station.station_id} - ${station.name}</option>`
    ).join('');
}

/**
 * Apply filter to tables
 */
function applyFilter(filterValue) {
    currentFilter = filterValue;
    
    // Update workers table visibility
    const workerRows = elements.workersTableBody.querySelectorAll('tr[data-worker-id]');
    workerRows.forEach(row => {
        if (filterValue === 'all' || filterValue.startsWith('station-')) {
            row.classList.remove('hidden');
        } else if (filterValue.startsWith('worker-')) {
            const workerId = filterValue.replace('worker-', '');
            row.classList.toggle('hidden', row.dataset.workerId !== workerId);
        }
    });
    
    // Update workstations table visibility
    const stationRows = elements.workstationsTableBody.querySelectorAll('tr[data-station-id]');
    stationRows.forEach(row => {
        if (filterValue === 'all' || filterValue.startsWith('worker-')) {
            row.classList.remove('hidden');
        } else if (filterValue.startsWith('station-')) {
            const stationId = filterValue.replace('station-', '');
            row.classList.toggle('hidden', row.dataset.stationId !== stationId);
        }
    });
    
    // Show/hide sections based on filter
    if (filterValue.startsWith('worker-')) {
        elements.workersSection.style.display = 'block';
        elements.workstationsSection.style.display = 'none';
    } else if (filterValue.startsWith('station-')) {
        elements.workersSection.style.display = 'none';
        elements.workstationsSection.style.display = 'block';
    } else {
        elements.workersSection.style.display = 'block';
        elements.workstationsSection.style.display = 'block';
    }
}

/**
 * Seed the database with sample data
 */
async function seedDatabase() {
    try {
        elements.seedBtn.disabled = true;
        elements.seedBtn.textContent = 'Seeding...';
        
        const response = await fetch(`${API_BASE_URL}/seed`, {
            method: 'POST'
        });
        
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        
        const data = await response.json();
        showStatus(`Database seeded: ${data.data.workers} workers, ${data.data.workstations} workstations, ${data.data.events} events`, 'success');
        
        // Refresh all data
        await loadAllData();
        
    } catch (error) {
        console.error('Error seeding database:', error);
        showStatus('Failed to seed database', 'error');
    } finally {
        elements.seedBtn.disabled = false;
        elements.seedBtn.textContent = 'Reset & Seed Data';
    }
}

/**
 * Load all data from the API
 */
async function loadAllData() {
    try {
        elements.refreshBtn.disabled = true;
        elements.refreshBtn.textContent = 'Loading...';
        
        await Promise.all([
            fetchFactoryMetrics(),
            fetchWorkerMetrics(),
            fetchWorkstationMetrics()
        ]);
        
        showStatus('Data refreshed successfully', 'success');
        
    } catch (error) {
        console.error('Error loading data:', error);
        showStatus('Failed to load some data', 'error');
    } finally {
        elements.refreshBtn.disabled = false;
        elements.refreshBtn.textContent = 'Refresh Data';
    }
}

/**
 * Initialize the application
 */
function init() {
    // Update API URL display
    elements.apiUrl.textContent = API_BASE_URL;
    
    // Event listeners
    elements.refreshBtn.addEventListener('click', loadAllData);
    elements.seedBtn.addEventListener('click', seedDatabase);
    elements.filterSelect.addEventListener('change', (e) => applyFilter(e.target.value));
    
    // Load initial data
    loadAllData();
}

// Start the application when DOM is ready
document.addEventListener('DOMContentLoaded', init);
