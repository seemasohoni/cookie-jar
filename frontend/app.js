const API_BASE_URL = 'http://localhost:8000';
const USER_ID = 'test-user-1';

// State
let state = {
    cookies: 0,
    progress: 0,
    target: 100,
    riskScores: Array(24).fill(0),
    patterns: { time_of_day: {}, triggers: {} }
};

// Chart Instances
let vulnChart = null;
let todChart = null;
let triggerChart = null;

// Initialization
document.addEventListener('DOMContentLoaded', () => {
    initChart();
    initPatternCharts();
    fetchStats();
    fetchVulnerability();
    fetchHabits();
    fetchPatterns();
    
    // Bind form event listeners exactly once DOM is ready
    document.getElementById('create-habit-form').addEventListener('submit', createHabit);
    document.getElementById('log-habit-form').addEventListener('submit', submitLogHabit);
    document.getElementById('edit-habit-form').addEventListener('submit', updateHabit);
    
    // Dashboard Filter Listener
    document.getElementById('habit-filter').addEventListener('change', () => {
        fetchVulnerability();
        fetchPatterns();
    });
    
    // Timescale Filter Listener
    document.getElementById('timescale-filter').addEventListener('change', () => {
        fetchVulnerability();
    });
    
    // Bind logic for custom trigger text input
    document.getElementById('log-trigger').addEventListener('change', (e) => {
        const customInput = document.getElementById('log-trigger-custom');
        if (e.target.value === 'CUSTOM') {
            customInput.classList.remove('hidden');
            customInput.required = true;
        } else {
            customInput.classList.add('hidden');
            customInput.required = false;
        }
    });
});

// Fetch user stats
async function fetchStats() {
    try {
        const res = await fetch(`${API_BASE_URL}/rewards/status?user_id=${USER_ID}`);
        if (!res.ok) throw new Error('Failed to fetch rewards');
        const data = await res.json();
        
        state.cookies = data.current_cookies;
        state.progress = data.current_progress;
        state.target = data.next_milestone_target;
        
        updateUI();
    } catch (err) {
        console.error('API Error:', err);
        // Fallback for visual testing
        updateUI();
    }
}

// Fetch vulnerability scores
async function fetchVulnerability() {
    try {
        const filterId = document.getElementById('habit-filter').value;
        const timescaleId = document.getElementById('timescale-filter').value;
        const query = filterId ? `&habit_id=${filterId}` : '';
        const timescaleQuery = timescaleId ? `&timescale=${timescaleId}` : '';
        
        const res = await fetch(`${API_BASE_URL}/analytics/vulnerability?user_id=${USER_ID}${query}${timescaleQuery}&_t=${Date.now()}`);
        if (!res.ok) throw new Error('Failed to fetch analytics');
        const data = await res.json();
        
        // Map data to array
        state.riskScores = Array.from({length: 24}, (_, i) => data[String(i)] || 0);
        updateChart();
    } catch (err) {
        console.error('API Error:', err);
    }
}

// Fetch pattern groupings
async function fetchPatterns() {
    try {
        const filterId = document.getElementById('habit-filter').value;
        const query = filterId ? `&habit_id=${filterId}` : '';
        
        const res = await fetch(`${API_BASE_URL}/analytics/patterns?user_id=${USER_ID}${query}&_t=${Date.now()}`);
        if (!res.ok) throw new Error('Failed to fetch patterns');
        state.patterns = await res.json();
        updatePatternCharts();
    } catch (err) {
        console.error('API Error:', err);
    }
}

// Fetch habits list
async function fetchHabits() {
    try {
        // Add cache busting to ensure we get fresh habits from the API
        const res = await fetch(`${API_BASE_URL}/habits?user_id=${USER_ID}&_t=${Date.now()}`);
        if (!res.ok) throw new Error('Failed to fetch habits');
        const habits = await res.json();
        renderHabits(habits);
        updateHabitFilterOptions(habits);
    } catch (err) {
        console.error('API Error:', err);
        alert("Failed to load habits. Is the API running?");
    }
}

// Dropdown synchronization
function updateHabitFilterOptions(habits) {
    const filter = document.getElementById('habit-filter');
    const currentValue = filter.value;
    
    // Reset but keep "All Habits"
    filter.innerHTML = '<option value="">All Habits</option>';
    
    habits.forEach(habit => {
        const option = document.createElement('option');
        option.value = habit.id;
        option.textContent = habit.name;
        filter.appendChild(option);
    });
    
    // Restore selection if it still exists
    if (habits.find(h => h.id === currentValue)) {
        filter.value = currentValue;
    }
}

// Render habits to UI
function renderHabits(habits) {
    const list = document.getElementById('habits-list');
    
    // Capture open logbooks before re-rendering
    const openLogbookIds = [];
    document.querySelectorAll('div[id^="logbook-"]').forEach(el => {
        if (!el.classList.contains('hidden')) {
            const id = el.id.replace('logbook-', '');
            openLogbookIds.push(id);
        }
    });

    list.innerHTML = '';
    habits.forEach(habit => {
        const div = document.createElement('div');
        div.className = 'habit-item';
        div.style.flexDirection = 'column';
        div.style.alignItems = 'stretch';
        div.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: center; width: 100%;">
                <div>
                    <strong>${habit.name}</strong>
                    <span class="badge ${habit.category === 'GOOD' ? 'badge-good' : 'badge-bad'}">${habit.category}</span>
                </div>
                <div style="display: flex; gap: 0.5rem;">
                    <button class="btn btn-sm" style="background-color: #64748b;" onclick="toggleLogbook('${habit.id}')">Logbook</button>
                    <button class="btn btn-sm" style="background-color: #475569;" onclick="openEditModal('${habit.id}', '${habit.name.replace(/'/g, "\\'")}', '${habit.category}', ${habit.target_daily || 1})">Edit</button>
                    <button class="btn btn-primary btn-sm" onclick="openLogModal('${habit.id}', '${habit.category}')">Log</button>
                </div>
            </div>
            <div id="logbook-${habit.id}" class="hidden" style="margin-top: 1rem; width: 100%; border-top: 1px solid #334155; padding-top: 0.5rem;">
                <table style="width: 100%; border-collapse: collapse; text-align: left; font-size: 0.85rem;">
                    <thead>
                        <tr>
                            <th style="padding: 0.5rem 0; color: #94a3b8;">Time</th>
                            <th style="padding: 0.5rem 0; color: #94a3b8;">Date</th>
                            <th style="padding: 0.5rem 0; color: #94a3b8;">Trigger</th>
                        </tr>
                    </thead>
                    <tbody id="logbook-body-${habit.id}">
                        <tr><td colspan="3" style="text-align: center;">Loading...</td></tr>
                    </tbody>
                </table>
            </div>
        `;
        list.appendChild(div);
    });
    
    // Restore open logbooks
    openLogbookIds.forEach(id => {
        const container = document.getElementById(`logbook-${id}`);
        if (container) {
            container.classList.remove('hidden');
            // Re-fetch the content for this specific logbook
            fetchLogbookData(id);
        }
    });
}

// Inline Logbook Logic
async function toggleLogbook(id) {
    const container = document.getElementById(`logbook-${id}`);
    
    if (container.classList.contains('hidden')) {
        container.classList.remove('hidden');
        await fetchLogbookData(id);
    } else {
        container.classList.add('hidden');
    }
}

async function fetchLogbookData(id) {
    const tbody = document.getElementById(`logbook-body-${id}`);
    tbody.innerHTML = '<tr><td colspan="3" style="text-align: center; color: #94a3b8;">Loading logs...</td></tr>';
    
    try {
        const res = await fetch(`${API_BASE_URL}/habits/${id}/logs?user_id=${USER_ID}&_t=${Date.now()}`);
        if (!res.ok) throw new Error('Failed to fetch habit history');
        
        const logs = await res.json();
        
        tbody.innerHTML = '';
        if (logs.length === 0) {
            tbody.innerHTML = '<tr><td colspan="3" style="text-align: center; color: #64748b; padding: 1rem 0;">No logs recorded yet.</td></tr>';
            return;
        }
        
        logs.forEach((log) => {
            const tr = document.createElement('tr');
            const d = new Date(log.timestamp);
            const timeStr = d.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
            const dateStr = d.toLocaleDateString();
            
            tr.innerHTML = `
                <td style="padding: 0.5rem 0;">${timeStr}</td>
                <td style="padding: 0.5rem 0; color: #cbd5e1;">${dateStr}</td>
                <td style="padding: 0.5rem 0;"><span class="badge" style="background-color: #334155; font-size: 0.70rem; padding: 0.2rem 0.5rem;">${log.trigger_type}</span></td>
            `;
            tbody.appendChild(tr);
        });
        
    } catch (err) {
        console.error('API Error:', err);
        tbody.innerHTML = '<tr><td colspan="3" style="text-align: center; color: #ef4444; padding: 1rem 0;">Error loading logs</td></tr>';
    }
}

// Edit Habit Modal Logic
function openEditModal(id, name, category, target) {
    document.getElementById('edit-habit-id').value = id;
    document.getElementById('edit-habit-name').value = name;
    document.getElementById('edit-habit-category').value = category;
    
    document.getElementById('edit-habit-modal').classList.remove('hidden');
}

function closeEditModal() {
    document.getElementById('edit-habit-modal').classList.add('hidden');
}

// Update Habit API Call
async function updateHabit(event) {
    event.preventDefault();
    const id = document.getElementById('edit-habit-id').value;
    const name = document.getElementById('edit-habit-name').value;
    const category = document.getElementById('edit-habit-category').value;
    
    try {
        const res = await fetch(`${API_BASE_URL}/habits/${id}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, category, target_daily: 1 })
        });
        
        if (!res.ok) throw new Error('Failed to update habit');
        
        closeEditModal();
        fetchHabits();
        fetchVulnerability();
        fetchPatterns();
    } catch (err) {
        console.error('API Error:', err);
        alert(err.message);
    }
}

// Delete Habit API Call
async function deleteHabit() {
    const id = document.getElementById('edit-habit-id').value;
    
    if (!confirm('Are you sure you want to completely delete this habit and all its logs? This cannot be undone.')) {
        return;
    }
    
    try {
        const res = await fetch(`${API_BASE_URL}/habits/${id}?user_id=${USER_ID}`, {
            method: 'DELETE'
        });
        
        if (!res.ok) throw new Error('Failed to delete habit');
        
        closeEditModal();
        
        // Reset Dropdown if the deleted habit was selected
        const filter = document.getElementById('habit-filter');
        if (filter.value === id) {
            filter.value = '';
        }
        
        // Refresh Everything
        fetchHabits();
        fetchVulnerability();
        fetchPatterns();
        fetchStats();
    } catch (err) {
        console.error('API Error:', err);
        alert(err.message);
    }
}

// Create a new habit
async function createHabit(event) {
    // Explicitly prevent form submission
    event.preventDefault();
    
    const nameInput = document.getElementById('new-habit-name');
    const categoryInput = document.getElementById('new-habit-category');
    
    const name = nameInput.value;
    const category = categoryInput.value;
    
    try {
        const res = await fetch(`${API_BASE_URL}/habits`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, category })
        });
        
        if (!res.ok) {
            throw new Error(`Server returned ${res.status}`);
        }
        
        nameInput.value = '';
        
        // Refetch and re-render dashboard
        await fetchHabits();
    } catch (err) {
        console.error('Error creating habit:', err);
        alert(`Could not create habit: ${err.message}`);
    }
}

// Modal handling
function openLogModal(habitId, category) {
    document.getElementById('log-habit-id').value = habitId;
    document.getElementById('log-habit-category').value = category;
    
    // Default to current local time without exact seconds (datetime-local requires specific format: YYYY-MM-DDThh:mm)
    const now = new Date();
    now.setMinutes(now.getMinutes() - now.getTimezoneOffset());
    document.getElementById('log-time').value = now.toISOString().slice(0, 16);
    
    // Reset inputs
    document.getElementById('log-trigger').value = 'MANUAL';
    document.getElementById('log-trigger-custom').classList.add('hidden');
    document.getElementById('log-trigger-custom').value = '';
    
    document.getElementById('log-modal').classList.remove('hidden');
}

function closeLogModal() {
    document.getElementById('log-modal').classList.add('hidden');
}

// Submit log
async function submitLogHabit(event) {
    event.preventDefault();
    const habitId = document.getElementById('log-habit-id').value;
    const category = document.getElementById('log-habit-category').value;
    const timeValue = document.getElementById('log-time').value;
    let trigger = document.getElementById('log-trigger').value;
    
    if (trigger === 'CUSTOM') {
        trigger = document.getElementById('log-trigger-custom').value;
    }
    
    const timestamp = new Date(timeValue).toISOString();
    
    // Optimistic UI update
    if (category === 'GOOD') {
        state.cookies++;
        state.progress = state.cookies % 100;
        updateUI();
    }
    
    try {
        await fetch(`${API_BASE_URL}/habits/log`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                habit_id: habitId,
                timestamp: timestamp,
                trigger_type: trigger
            })
        });
        
        closeLogModal();
        fetchPatterns(); // Refresh patterns
        fetchHabits(); // Refresh logbooks smoothly
        
        if (category === 'BAD') {
            fetchVulnerability();
        }
    } catch (err) {
        console.error('Error logging habit:', err);
    }
}

// Update DOM elements
function updateUI() {
    document.getElementById('total-cookies').textContent = state.cookies;
    document.getElementById('progress-cookies').textContent = `${state.progress} / ${state.target}`;
    
    // Update the visual jar
    const fillPercentage = Math.min((state.progress / state.target) * 100, 100);
    document.getElementById('cookie-fill').style.height = `${fillPercentage}%`;
}

// Initialize Chart.js graph
function initChart() {
    const ctx = document.getElementById('vulnerabilityChart').getContext('2d');
    
    // Labels for 24 hours (e.g., 12AM, 1AM...)
    const labels = Array.from({length: 24}, (_, i) => {
        const ampm = i >= 12 ? 'PM' : 'AM';
        const hr = i % 12 || 12;
        return `${hr}${ampm}`;
    });

    vulnChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Risk Score',
                data: state.riskScores,
                borderColor: '#ef4444',
                backgroundColor: 'rgba(239, 68, 68, 0.2)',
                borderWidth: 2,
                fill: true,
                tension: 0.4,
                pointBackgroundColor: '#1e293b',
                pointBorderColor: '#ef4444',
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: {
                    beginAtZero: true,
                    max: 1.0,
                    grid: { color: 'rgba(255, 255, 255, 0.1)' },
                    ticks: { color: '#94a3b8' }
                },
                x: {
                    grid: { display: false },
                    ticks: { color: '#94a3b8', maxTicksLimit: 8 }
                }
            },
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `Risk: ${(context.raw * 100).toFixed(0)}%`;
                        }
                    }
                }
            }
        }
    });
}

// Update chart with new data
function updateChart() {
    if (vulnChart) {
        vulnChart.data.datasets[0].data = state.riskScores;
        vulnChart.update();
    }
}

// Initialize Pattern Charts
function initPatternCharts() {
    const timeCtx = document.getElementById('timeOfDayChart').getContext('2d');
    const triggerCtx = document.getElementById('triggerTypeChart').getContext('2d');
    
    const commonOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
            legend: {
                position: 'right',
                labels: { color: '#94a3b8' }
            }
        }
    };

    todChart = new Chart(timeCtx, {
        type: 'doughnut',
        data: { labels: [], datasets: [{ data: [], backgroundColor: ['#3b82f6', '#f59e0b', '#8b5cf6', '#1e293b'], borderColor: '#0f172a' }] },
        options: commonOptions
    });
    
    triggerChart = new Chart(triggerCtx, {
        type: 'pie',
        data: { labels: [], datasets: [{ data: [], backgroundColor: ['#ef4444', '#10b981', '#6366f1', '#f43f5e', '#84cc16', '#a855f7'], borderColor: '#0f172a' }] },
        options: commonOptions
    });
}

// Update pattern charts with new data
function updatePatternCharts() {
    if (!state.patterns) return;
    
    // Time of day
    if (todChart && state.patterns.time_of_day) {
        todChart.data.labels = Object.keys(state.patterns.time_of_day);
        todChart.data.datasets[0].data = Object.values(state.patterns.time_of_day);
        todChart.update();
    }
    
    // Triggers
    if (triggerChart && state.patterns.triggers) {
        triggerChart.data.labels = Object.keys(state.patterns.triggers);
        triggerChart.data.datasets[0].data = Object.values(state.patterns.triggers);
        triggerChart.update();
    }
}
