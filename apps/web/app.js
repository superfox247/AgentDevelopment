/**
 * app.js
 * Main controller for the Debug Dashboard.
 */

const timeline = new TimelineRenderer('timeline-feed');
const triggerBtn = document.getElementById('trigger-btn');
const topicInput = document.getElementById('topic-input');

// Stats Elements
const elStatus = document.getElementById('status-badge');
const elEventCount = document.getElementById('event-count');
const elTimer = document.getElementById('duration-timer');
const elTokenCount = document.getElementById('token-count');
const elTraceLink = document.getElementById('trace-link');

let isGenerating = false;
let eventCounter = 0;
let tokenCounter = 0;
let startTime = null;
let timerInterval = null;

function setStatus(status) {
    elStatus.className = 'badge ' + (status === 'Generating' ? 'active' : (status === 'Complete' ? 'success' : 'idle'));
    elStatus.textContent = status;
}

function startTimer() {
    startTime = Date.now();
    clearInterval(timerInterval);
    timerInterval = setInterval(() => {
        const diff = Math.floor((Date.now() - startTime) / 1000);
        const m = Math.floor(diff / 60).toString().padStart(2, '0');
        const s = (diff % 60).toString().padStart(2, '0');
        elTimer.textContent = `${m}:${s}`;
    }, 1000);
}

function stopTimer() {
    clearInterval(timerInterval);
}

triggerBtn.addEventListener('click', async () => {
    if (isGenerating) return;

    // Reset
    timeline.reset();
    setStatus('Generating');
    triggerBtn.disabled = true;
    triggerBtn.querySelector('.spinner').classList.remove('hidden');
    eventCounter = 0;
    tokenCounter = 0;
    elEventCount.textContent = '0';
    elTokenCount.textContent = '0';
    elTraceLink.href = '#';
    elTraceLink.textContent = 'Waiting for Trace...';

    startTimer();

    const topic = topicInput.value;
    const sessionId = 'session-' + Math.random().toString(36).substring(2, 9);

    try {
        // --- 1. Call API ---
        const response = await fetch('/api/chat_stream', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                message: `Create a course on: ${topic}`,
                session_id: sessionId
            })
        });

        if (!response.ok) throw new Error("API Error");

        // --- 2. Stream Reader ---
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';

        while (true) {
            const { value, done } = await reader.read();
            if (done) break;

            buffer += decoder.decode(value, { stream: true });
            const lines = buffer.split('\n');
            buffer = lines.pop(); // Keep incomplete line

            for (const line of lines) {
                if (!line.trim()) continue;
                try {
                    const data = JSON.parse(line);
                    handleEvent(data);
                } catch (e) {
                    console.error("JSON Parse Error", e);
                }
            }
        }

        setStatus('Complete');

    } catch (err) {
        console.error(err);
        setStatus('Error');
        timeline.addEvent({
            type: 'error',
            agent: 'System',
            message: `Connection failed: ${err.message}`,
            status: 'error'
        });
    } finally {
        isGenerating = false;
        triggerBtn.disabled = false;
        triggerBtn.querySelector('.spinner').classList.add('hidden');
        stopTimer();
    }
});

function handleEvent(data) {
    eventCounter++;
    elEventCount.textContent = eventCounter;

    // TODO: The backend needs to send structured events.
    // Currently the legacy backend sends: { type: 'progress', text: '...' }
    // We will adapt it to our timeline format.

    let timelineEvent = {
        timestamp: Date.now(),
        agent: 'Orchestrator',
        type: 'log',
        message: data.text || JSON.stringify(data),
        tokens: 0,
        cost: 0
    };

    // Map backend types to timeline types
    if (data.type === 'tool_use') {
        timelineEvent.type = 'tool';
        timelineEvent.agent = data.agent;
        timelineEvent.message = data.text; // "Calling search_tool..."
        timelineEvent.args = data.args;    // JSON string of arguments
    } else if (data.type === 'agent_thought') {
        timelineEvent.type = 'agent';
        timelineEvent.agent = data.agent;
        timelineEvent.message = data.text;
        timelineEvent.tokens = data.tokens;
        timelineEvent.cost = data.cost;

        // Accumulate totals
        if (data.tokens) tokenCounter += data.tokens;
        elTokenCount.textContent = tokenCounter.toLocaleString();
    } else if (data.type === 'progress') {
        // Fallback for any legacy events
        timelineEvent.type = 'agent';
        timelineEvent.message = data.text;
    }

    // Telemetry Update (Mock for now until backend sends it)
    if (data.trace_id && elTraceLink.textContent === 'Waiting for Trace...') {
        elTraceLink.href = `http://localhost:6006/traces/${data.trace_id}`;
        elTraceLink.textContent = data.trace_id.substring(0, 8) + '...';
    }

    timeline.addEvent(timelineEvent);
}
