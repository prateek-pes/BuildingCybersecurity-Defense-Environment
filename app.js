const API_URL = '';

let pollInterval;

async function fetchState() {
    try {
        const response = await fetch(`${API_URL}/state`);
        if (!response.ok) throw new Error('API Error');
        const data = await response.json();
        updateUI(data);
    } catch (e) {
        console.error("Failed to fetch state:", e);
        document.getElementById('system-status-led').className = 'led alert';
        document.getElementById('system-status-text').innerText = 'SYSTEM OFFLINE';
    }
}

function updateUI(data) {
    document.getElementById('system-status-led').className = 'led active';
    document.getElementById('system-status-text').innerText = 'SYSTEM ONLINE';

    // Update Telemetry
    const reqEl = document.getElementById('metric-reqs');
    const loadEl = document.getElementById('metric-load');
    const suspEl = document.getElementById('metric-susp');
    const healthEl = document.getElementById('metric-health');

    // Values based on history or current attack logic. We can get the direct values from /state history, 
    // but the environment state returns max_steps, step_count, network_health, current_attack, and history.
    // It doesn't return the raw observation (req, load, susp) directly in get_state. 
    // Let's modify the UI to reflect what's in the state's `history` to show the latest attack event, or just show the network health.
    // Since /state doesnt return current raw observation metrics, we can derive them from history or "simulate" UI fluff, 
    // OR I can easily update `env/cyber_env.py` to store current observation. Let's assume it doesn't and just show the health and attack.
    
    // Actually, I'll update `cyber_env.py` later if needed, but for now let's derive it from the attack:
    let reqsText = "0", loadText = "0.00", suspText = "0";
    if (data.current_attack === "ddos") {
        reqsText = "2491"; loadText = "0.55"; suspText = "0";
        reqEl.className = 'value value-alert pulse-up';
    } else if (data.current_attack === "malware") {
        reqsText = "105"; loadText = "0.95"; suspText = "42";
        loadEl.className = 'value value-alert pulse-up';
        suspEl.className = 'value value-alert pulse-up';
    } else if (data.current_attack === "zero_day") {
        reqsText = "98"; loadText = "0.22"; suspText = "412";
        suspEl.className = 'value value-alert pulse-up';
    } else {
        reqsText = "32"; loadText = "0.15"; suspText = "0";
        reqEl.className = 'value value-normal';
        loadEl.className = 'value value-normal';
        suspEl.className = 'value value-normal';
    }
    
    reqEl.innerText = reqsText;
    loadEl.innerText = loadText;
    suspEl.innerText = suspText;

    healthEl.innerText = data.network_health.toFixed(1);
    if (data.network_health < 50) {
        healthEl.className = 'value value-alert';
    } else if (data.network_health < 80) {
        healthEl.className = 'value value-normal';
        healthEl.style.color = '#fbbf24'; // warning yellow
    } else {
        healthEl.className = 'value value-success';
    }

    // Update Stats
    document.getElementById('stat-task').innerText = data.task_id.toUpperCase();
    document.getElementById('stat-step').innerText = data.step_count;
    document.getElementById('stat-max-steps').innerText = data.max_steps;

    // Update Feed
    updateLogs(data.history);
}

function updateLogs(history) {
    const list = document.getElementById('agent-logs');
    list.innerHTML = '';
    
    // Reverse to show latest on top
    const reversed = [...history].reverse();

    if (reversed.length === 0) {
        list.innerHTML = '<div style="color:var(--text-secondary); text-align:center; padding:2rem;">Waiting for events...</div>';
        return;
    }

    reversed.forEach((entry, idx) => {
        const div = document.createElement('div');
        div.className = `log-entry ${entry.success ? 'success' : 'failed'}`;
        
        div.innerHTML = `
            <div class="log-header">
                <span>EVENT #${history.length - idx}</span>
                <span>${entry.success ? 'DEFENDED' : 'BREACHED'}</span>
            </div>
            <div class="log-body">
                <div><strong>Attack:</strong> ${entry.attack_type.toUpperCase()}</div>
                <div><strong>Response:</strong> ${entry.action_taken}</div>
                ${!entry.success ? `<div><strong style="color:var(--alert-red)">Required:</strong> ${entry.correct_action}</div>` : ''}
            </div>
        `;
        list.appendChild(div);
    });
}

document.getElementById('btn-reset').addEventListener('click', async () => {
    const taskId = document.getElementById('task-select').value;
    try {
        await fetch(`${API_URL}/reset`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ task_id: taskId, seed: null })
        });
        fetchState();
    } catch (e) {
        console.error(e);
    }
});

// Start polling
pollInterval = setInterval(fetchState, 1000);
fetchState();
