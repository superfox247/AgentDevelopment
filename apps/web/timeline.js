/**
 * timeline.js
 * Handles rendering of events onto the timeline.
 */

class TimelineRenderer {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.events = [];
        this.startTime = null;
    }

    reset() {
        this.container.innerHTML = '';
        this.events = [];
        this.startTime = null;
    }

    addEvent(eventData) {
        if (!this.startTime) this.startTime = new Date(eventData.timestamp || Date.now());

        const item = this.renderItem(eventData);
        this.container.appendChild(item);
        this.events.push(eventData);

        // Smart Auto-scroll (only if near bottom)
        const isNearBottom = this.container.scrollHeight - this.container.scrollTop - this.container.clientHeight < 100;
        if (isNearBottom || this.events.length === 1) {
            this.container.scrollTop = this.container.scrollHeight;
        }
    }

    renderItem(data) {
        // Create Wrapper (Grid Layout)
        const item = document.createElement('div');
        item.className = 'event-item';
        item.dataset.agent = (data.agent || '').toLowerCase();
        item.dataset.type = data.type || 'log';
        item.dataset.status = data.status || 'success';

        // 1. Time Column
        const timeCol = document.createElement('div');
        timeCol.className = 'time-col';
        const time = new Date(data.timestamp || Date.now());

        const timeStr = document.createElement('div');
        timeStr.textContent = time.toLocaleTimeString([], { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' });

        const latencyStr = document.createElement('div');
        latencyStr.className = 'latency';
        if (this.startTime) {
            latencyStr.textContent = `+${((time - this.startTime) / 1000).toFixed(1)}s`;
        } else {
            latencyStr.textContent = '+0.0s';
        }

        timeCol.appendChild(timeStr);
        timeCol.appendChild(latencyStr);

        // 2. Marker Column
        const markerCol = document.createElement('div');
        markerCol.className = 'marker-col';
        const line = document.createElement('div');
        line.className = 'line';
        const marker = document.createElement('div');
        marker.className = 'marker';
        markerCol.appendChild(line);
        markerCol.appendChild(marker);

        // 3. Content Column
        const contentCol = document.createElement('div');
        contentCol.className = 'content-col';

        const card = document.createElement('div');
        card.className = 'event-card';

        // Card Header
        const header = document.createElement('div');
        header.className = 'card-header';

        const agentInfo = document.createElement('div');
        agentInfo.className = 'agent-info';
        const name = document.createElement('span');
        name.className = 'agent-name';
        name.textContent = data.agent || 'System';

        const typeTag = document.createElement('span');
        typeTag.className = 'tag';
        typeTag.textContent = data.type === 'tool' ? 'TOOL USE' : (data.type === 'error' ? 'ERROR' : 'AGENT');

        agentInfo.appendChild(name);
        agentInfo.appendChild(typeTag);
        header.appendChild(agentInfo);

        if (data.status === 'error') {
            const errBadge = document.createElement('span');
            errBadge.className = 'badge error';
            errBadge.textContent = 'Failed';
            header.appendChild(errBadge);
        }

        // Card Body
        const body = document.createElement('div');
        body.className = 'card-body';

        if (data.type === 'tool') {
            body.innerHTML = `<div><strong>Frequency:</strong> Calling <code>${data.message}</code></div>`;
            if (data.args && data.args !== "{}") {
                body.innerHTML += `<pre>${this.escapeHtml(data.args)}</pre>`;
            }
        } else {
            // Simple Markdown rendering
            body.innerHTML = this.parseMarkdown(data.message || '');
        }

        // Card Footer (Metadata)
        if (data.tokens || data.cost) {
            const footer = document.createElement('div');
            footer.className = 'card-footer';

            if (data.tokens) {
                footer.innerHTML += `<div class="meta-tag">🪙 ${data.tokens.toLocaleString()} toks</div>`;
            }
            if (data.cost) {
                footer.innerHTML += `<div class="meta-tag">💰 $${data.cost.toFixed(5)}</div>`;
            }
            card.appendChild(footer);
        }

        card.appendChild(header);
        card.appendChild(body);
        contentCol.appendChild(card);

        item.appendChild(timeCol);
        item.appendChild(markerCol);
        item.appendChild(contentCol);

        return item;
    }

    escapeHtml(unsafe) {
        return unsafe.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;").replace(/'/g, "&#039;");
    }

    parseMarkdown(text) {
        // Very simple markdown parser for bold, headers, and code
        let html = this.escapeHtml(text);
        html = html.replace(/\n/g, '<br>');
        html = html.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        html = html.replace(/`(.*?)`/g, '<code>$1</code>');
        html = html.replace(/### (.*?)(<br>|$)/g, '<h3>$1</h3>');
        html = html.replace(/## (.*?)(<br>|$)/g, '<h2>$1</h2>');
        html = html.replace(/# (.*?)(<br>|$)/g, '<h1>$1</h1>');
        return html;
    }
}
