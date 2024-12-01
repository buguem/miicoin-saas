// Fetch and update trading signals
async function updateSignals() {
    try {
        const response = await fetch('/api/signals');
        const data = await response.json();
        
        const signalsList = document.getElementById('signals-list');
        if (signalsList) {
            signalsList.innerHTML = data.signals.map(signal => `
                <div class="signal">
                    <strong>${signal.symbol}</strong>
                    <span class="${signal.type.toLowerCase()}">${signal.type}</span>
                    <span>Price: ${signal.price}</span>
                    <span>Time: ${new Date(signal.timestamp).toLocaleString()}</span>
                </div>
            `).join('');
        }
    } catch (error) {
        console.error('Error fetching signals:', error);
    }
}

// Fetch and update bot status
async function updateBotStatus() {
    try {
        const response = await fetch('/api/bot/status');
        const data = await response.json();
        
        const botStatus = document.getElementById('bot-status');
        if (botStatus) {
            botStatus.innerHTML = `
                <div class="status-item">
                    <strong>Status:</strong> ${data.status}
                </div>
                <div class="status-item">
                    <strong>Active Trades:</strong> ${data.active_trades}
                </div>
                <div class="status-item">
                    <strong>Last Trade:</strong> ${data.last_trade || 'None'}
                </div>
            `;
        }
    } catch (error) {
        console.error('Error fetching bot status:', error);
    }
}

// Update data periodically
function startUpdates() {
    // Update immediately
    updateSignals();
    updateBotStatus();
    
    // Then update every 30 seconds
    setInterval(() => {
        updateSignals();
        updateBotStatus();
    }, 30000);
}

// Start updates when the page loads
document.addEventListener('DOMContentLoaded', startUpdates);
