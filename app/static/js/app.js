document.addEventListener('DOMContentLoaded', function() {

    initSidebar();
    initTheme();
    initNotifications();
    initAlerts();
    initSmartSearch();
    initAiAssistant();

    var charts = document.querySelectorAll('.chart-container');
    if (charts.length > 0) initCharts();

});

function initSidebar() {
    var toggle = document.getElementById('sidebarToggle');
    var sidebar = document.getElementById('sidebar');
    var overlay = document.getElementById('sidebarOverlay');

    if (toggle && sidebar) {
        toggle.addEventListener('click', function(e) {
            e.stopPropagation();
            if (window.innerWidth <= 768) {
                sidebar.classList.toggle('open');
                if (overlay) overlay.classList.toggle('show');
            } else {
                sidebar.classList.toggle('collapsed');
            }
        });
    }

    if (overlay) {
        overlay.addEventListener('click', function() {
            sidebar.classList.remove('open');
            overlay.classList.remove('show');
        });
    }

    var navItems = document.querySelectorAll('.nav-item');
    navItems.forEach(function(item) {
        item.addEventListener('click', function() {
            var link = this.getAttribute('href');
            if (link && !this.classList.contains('active')) {
                window.location.href = link;
            }
        });
    });
}

function initTheme() {
    var savedTheme = localStorage.getItem('dashboard-theme') || document.documentElement.getAttribute('data-theme') || 'light';
    applyTheme(savedTheme);

    var themeBtns = document.querySelectorAll('.theme-btn');
    themeBtns.forEach(function(btn) {
        btn.addEventListener('click', function() {
            var theme = this.getAttribute('data-theme');
            applyTheme(theme);
            localStorage.setItem('dashboard-theme', theme);

            fetch('/settings/theme', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                    'X-CSRFToken': getCSRFToken()
                },
                body: 'theme=' + theme
            });
        });
    });
}

function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
    var themeBtns = document.querySelectorAll('.theme-btn');
    themeBtns.forEach(function(btn) {
        btn.classList.toggle('active', btn.getAttribute('data-theme') === theme);
    });
}

function getCSRFToken() {
    var meta = document.querySelector('meta[name="csrf-token"]');
    return meta ? meta.getAttribute('content') : '';
}

function initNotifications() {
    var notifBtn = document.getElementById('notifBtn');
    var notifDropdown = document.getElementById('notifDropdown');

    if (notifBtn && notifDropdown) {
        notifBtn.addEventListener('click', function(e) {
            e.stopPropagation();
            notifDropdown.classList.toggle('show');
        });

        document.addEventListener('click', function(e) {
            if (!notifDropdown.contains(e.target) && !notifBtn.contains(e.target)) {
                notifDropdown.classList.remove('show');
            }
        });
    }

    var markReadBtns = document.querySelectorAll('.mark-read');
    markReadBtns.forEach(function(btn) {
        btn.addEventListener('click', function() {
            var id = this.getAttribute('data-id');
            fetch('/api/notifications/read/' + id, {
                method: 'POST',
                headers: {
                    'X-CSRFToken': getCSRFToken()
                }
            }).then(function() {
                var item = this.closest('.notif-item');
                if (item) item.classList.remove('notif-unread');
                updateNotifBadge();
            }.bind(this));
        });
    });

    var markAllBtn = document.getElementById('markAllRead');
    if (markAllBtn) {
        markAllBtn.addEventListener('click', function() {
            fetch('/api/notifications/read-all', {
                method: 'POST',
                headers: { 'X-CSRFToken': getCSRFToken() }
            }).then(function() {
                document.querySelectorAll('.notif-unread').forEach(function(el) {
                    el.classList.remove('notif-unread');
                });
                updateNotifBadge();
            });
        });
    }
}

function updateNotifBadge() {
    var unread = document.querySelectorAll('.notif-unread').length;
    var badges = document.querySelectorAll('.badge-dot, .nav-badge');
    badges.forEach(function(b) {
        if (b.classList.contains('nav-badge')) {
            b.textContent = unread;
            b.style.display = unread > 0 ? 'inline' : 'none';
        }
    });
}

function initAlerts() {
    document.querySelectorAll('.alert-dismiss').forEach(function(btn) {
        btn.addEventListener('click', function() {
            this.closest('.alert').remove();
        });
    });

    setTimeout(function() {
        document.querySelectorAll('.alert').forEach(function(alert) {
            alert.style.transition = 'opacity 0.5s ease';
            alert.style.opacity = '0';
            setTimeout(function() { alert.remove(); }, 500);
        });
    }, 5000);
}

function initSmartSearch() {
    var searchInput = document.getElementById('headerSearchInput');
    var searchResults = document.getElementById('searchResults');

    if (!searchInput || !searchResults) return;

    var debounceTimer;

    searchInput.addEventListener('input', function() {
        clearTimeout(debounceTimer);
        var query = this.value.trim();

        if (query.length < 2) {
            searchResults.classList.remove('show');
            searchResults.innerHTML = '';
            return;
        }

        debounceTimer = setTimeout(function() {
            fetch('/api/ai/smart-search?q=' + encodeURIComponent(query))
                .then(function(res) { return res.json(); })
                .then(function(data) {
                    if (data.results && data.results.length > 0) {
                        searchResults.innerHTML = data.results.map(function(r) {
                            return '<a href="' + r.url + '" class="search-result-item">' +
                                '<span class="search-result-type">' + r.type + '</span>' +
                                '<span class="search-result-title">' + escapeHtml(r.title) + '</span>' +
                                '<span class="search-result-subtitle">' + escapeHtml(r.subtitle) + '</span>' +
                                '</a>';
                        }).join('');
                        searchResults.classList.add('show');
                    } else {
                        searchResults.innerHTML = '<div class="search-result-empty">No results found</div>';
                        searchResults.classList.add('show');
                    }
                });
        }, 300);
    });

    document.addEventListener('click', function(e) {
        if (!searchResults.contains(e.target) && e.target !== searchInput) {
            searchResults.classList.remove('show');
        }
    });
}

function escapeHtml(text) {
    var div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function initAiAssistant() {
    var chatMessages = document.getElementById('chatMessages');
    var chatInput = document.getElementById('chatInput');
    var chatSend = document.getElementById('chatSend');

    if (!chatMessages || !chatInput || !chatSend) return;

    chatSend.addEventListener('click', function() {
        sendChatMessage();
    });

    chatInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            sendChatMessage();
        }
    });

    function sendChatMessage() {
        var message = chatInput.value.trim();
        if (!message) return;

        addChatMessage(message, 'user');
        chatInput.value = '';
        chatSend.disabled = true;
        chatSend.textContent = '...';

        fetch('/api/ai/assistant', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': getCSRFToken()
            },
            body: JSON.stringify({ message: message })
        })
        .then(function(res) { return res.json(); })
        .then(function(data) {
            addChatMessage(data.response, 'ai');
        })
        .catch(function() {
            addChatMessage('Sorry, I encountered an error. Please try again.', 'ai');
        })
        .finally(function() {
            chatSend.disabled = false;
            chatSend.textContent = 'Send';
        });
    }

    function addChatMessage(text, sender) {
        var div = document.createElement('div');
        div.className = 'chat-message ' + sender;

        var avatar = document.createElement('div');
        avatar.className = 'chat-avatar ' + sender;
        avatar.textContent = sender === 'ai' ? 'AI' : 'U';

        var bubble = document.createElement('div');
        bubble.className = 'chat-bubble';
        bubble.innerHTML = text.replace(/\n/g, '<br>');

        div.appendChild(avatar);
        div.appendChild(bubble);
        chatMessages.appendChild(div);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
}

function initCharts() {
    var revenueChart = document.getElementById('revenueChart');
    if (revenueChart) loadRevenueChart(revenueChart);

    var salesChart = document.getElementById('salesChart');
    if (salesChart) loadSalesChart(salesChart);

    var categoryChart = document.getElementById('categoryChart');
    if (categoryChart) loadCategoryChart(categoryChart);
}

function loadRevenueChart(canvas) {
    fetch('/api/revenue-chart')
        .then(function(r) { return r.json(); })
        .then(function(data) {
            if (data.labels && data.labels.length > 0) {
                drawBarChart(canvas, data.labels, data.values, '#4361ee');
            }
        });
}

function loadSalesChart(canvas) {
    fetch('/api/sales-chart')
        .then(function(r) { return r.json(); })
        .then(function(data) {
            if (data.labels && data.labels.length > 0) {
                var shortLabels = data.labels.map(function(l) { return l.slice(-5); });
                drawLineChart(canvas, shortLabels, data.values, '#7209b7');
            }
        });
}

function loadCategoryChart(canvas) {
    fetch('/api/category-chart')
        .then(function(r) { return r.json(); })
        .then(function(data) {
            if (data.labels && data.labels.length > 0) {
                drawDoughnutChart(canvas, data.labels, data.values);
            }
        });
}

function drawBarChart(canvas, labels, values, color) {
    var ctx = canvas.getContext('2d');
    var dpr = window.devicePixelRatio || 1;
    var rect = canvas.getBoundingClientRect();
    canvas.width = rect.width * dpr;
    canvas.height = rect.height * dpr;
    ctx.scale(dpr, dpr);

    var w = rect.width, h = rect.height;
    var padding = { top: 20, right: 20, bottom: 40, left: 50 };
    var chartW = w - padding.left - padding.right;
    var chartH = h - padding.top - padding.bottom;

    var maxVal = Math.max.apply(null, values) * 1.15;
    if (maxVal === 0) maxVal = 1;
    var barWidth = (chartW / labels.length) * 0.6;
    var gap = (chartW / labels.length);

    function getStyle(prop) {
        return getComputedStyle(document.documentElement).getPropertyValue(prop).trim();
    }

    var textColor = getStyle('--text-secondary') || '#6c757d';

    ctx.clearRect(0, 0, w, h);

    ctx.fillStyle = textColor;
    ctx.font = '10px sans-serif';
    ctx.textAlign = 'right';

    var steps = 5;
    for (var i = 0; i <= steps; i++) {
        var yVal = (maxVal / steps) * i;
        var y = padding.top + chartH - (chartH / steps) * i;
        ctx.fillText(formatNum(yVal), padding.left - 8, y + 4);
        ctx.strokeStyle = getStyle('--border-color') || '#eee';
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(padding.left, y);
        ctx.lineTo(w - padding.right, y);
        ctx.stroke();
    }

    ctx.textAlign = 'center';

    labels.forEach(function(label, i) {
        var x = padding.left + gap * i + gap / 2;
        var barH = (values[i] / maxVal) * chartH;
        var y = padding.top + chartH - barH;

        var gradient = ctx.createLinearGradient(0, y, 0, padding.top + chartH);
        gradient.addColorStop(0, color);
        gradient.addColorStop(1, color + '44');
        ctx.fillStyle = gradient;

        var radius = 4;
        ctx.beginPath();
        ctx.moveTo(x - barWidth / 2 + radius, y);
        ctx.lineTo(x + barWidth / 2 - radius, y);
        ctx.quadraticCurveTo(x + barWidth / 2, y, x + barWidth / 2, y + radius);
        ctx.lineTo(x + barWidth / 2, padding.top + chartH);
        ctx.lineTo(x - barWidth / 2, padding.top + chartH);
        ctx.lineTo(x - barWidth / 2, y + radius);
        ctx.quadraticCurveTo(x - barWidth / 2, y, x - barWidth / 2 + radius, y);
        ctx.fill();

        ctx.fillStyle = textColor;
        ctx.font = '10px sans-serif';
        ctx.fillText(label, x, w - (w - padding.left) / labels.length > 10 ? padding.bottom + 5 : padding.bottom + 60);
    });
}

function drawLineChart(canvas, labels, values, color) {
    var ctx = canvas.getContext('2d');
    var dpr = window.devicePixelRatio || 1;
    var rect = canvas.getBoundingClientRect();
    canvas.width = rect.width * dpr;
    canvas.height = rect.height * dpr;
    ctx.scale(dpr, dpr);

    var w = rect.width, h = rect.height;
    var padding = { top: 20, right: 20, bottom: 40, left: 50 };
    var chartW = w - padding.left - padding.right;
    var chartH = h - padding.top - padding.bottom;

    var maxVal = Math.max.apply(null, values) * 1.15;
    if (maxVal === 0) maxVal = 1;

    function getStyle(prop) {
        return getComputedStyle(document.documentElement).getPropertyValue(prop).trim();
    }

    var textColor = getStyle('--text-secondary') || '#6c757d';
    ctx.clearRect(0, 0, w, h);

    var steps = 4;
    ctx.fillStyle = textColor;
    ctx.font = '10px sans-serif';
    ctx.textAlign = 'right';

    for (var i = 0; i <= steps; i++) {
        var yVal = (maxVal / steps) * i;
        var y = padding.top + chartH - (chartH / steps) * i;
        ctx.fillText(Math.round(yVal), padding.left - 8, y + 4);
        ctx.strokeStyle = getStyle('--border-color') || '#eee';
        ctx.lineWidth = 1;
        ctx.beginPath();
        ctx.moveTo(padding.left, y);
        ctx.lineTo(w - padding.right, y);
        ctx.stroke();
    }

    var points = [];
    values.forEach(function(val, i) {
        var x = padding.left + (chartW / (values.length - 1 || 1)) * i;
        var y = padding.top + chartH - (val / maxVal) * chartH;
        points.push({ x: x, y: y });
    });

    ctx.strokeStyle = color;
    ctx.lineWidth = 3;
    ctx.lineJoin = 'round';
    ctx.lineCap = 'round';
    ctx.beginPath();
    points.forEach(function(p, i) {
        if (i === 0) ctx.moveTo(p.x, p.y);
        else {
            var cpx = (points[i - 1].x + p.x) / 2;
            var cpy = (points[i - 1].y + p.y) / 2;
            ctx.quadraticCurveTo(points[i - 1].x, points[i - 1].y, cpx, cpy);
        }
    });
    ctx.stroke();

    points.forEach(function(p) {
        ctx.fillStyle = color;
        ctx.beginPath();
        ctx.arc(p.x, p.y, 4, 0, Math.PI * 2);
        ctx.fill();
        ctx.fillStyle = '#fff';
        ctx.beginPath();
        ctx.arc(p.x, p.y, 2, 0, Math.PI * 2);
        ctx.fill();
    });

    ctx.fillStyle = textColor;
    ctx.font = '9px sans-serif';
    ctx.textAlign = 'center';
    var step = Math.max(1, Math.floor(labels.length / 7));
    labels.forEach(function(label, i) {
        if (i % step === 0 || i === labels.length - 1) {
            var x = padding.left + (chartW / (labels.length - 1 || 1)) * i;
            ctx.fillText(label, x, h - 8);
        }
    });
}

function drawDoughnutChart(canvas, labels, values) {
    var ctx = canvas.getContext('2d');
    var dpr = window.devicePixelRatio || 1;
    var rect = canvas.getBoundingClientRect();
    canvas.width = rect.width * dpr;
    canvas.height = rect.height * dpr;
    ctx.scale(dpr, dpr);

    var w = rect.width, h = rect.height;
    var cx = w / 2, cy = h / 2;
    var outerR = Math.min(w, h) * 0.38;
    var innerR = outerR * 0.6;

    var colors = ['#4361ee', '#7209b7', '#f72585', '#4cc9f0', '#06d6a0', '#ffd166', '#ef476f', '#4895ef'];
    var total = values.reduce(function(a, b) { return a + b; }, 0);
    if (total === 0) {
        ctx.fillStyle = '#eee';
        ctx.beginPath();
        ctx.arc(cx, cy, outerR, 0, Math.PI * 2);
        ctx.arc(cx, cy, innerR, 0, Math.PI * 2, true);
        ctx.fill();
        ctx.fillStyle = '#999';
        ctx.font = '16px sans-serif';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText('No data', cx, cy);
        return;
    }

    var startAngle = -Math.PI / 2;
    values.forEach(function(val, i) {
        var slice = (val / total) * Math.PI * 2;
        ctx.beginPath();
        ctx.arc(cx, cy, outerR, startAngle, startAngle + slice);
        ctx.arc(cx, cy, innerR, startAngle + slice, startAngle, true);
        ctx.closePath();
        ctx.fillStyle = colors[i % colors.length];
        ctx.fill();
        startAngle += slice;
    });

    ctx.fillStyle = getComputedStyle(document.documentElement).getPropertyValue('--text-primary').trim() || '#333';
    ctx.font = 'bold 18px sans-serif';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(total, cx, cy);

    var legendY = h - 20;
    var legendX = cx - (labels.length * 60) / 2;
    if (labels.length <= 4) {
        ctx.font = '10px sans-serif';
        labels.forEach(function(label, i) {
            var x = legendX + i * 60;
            ctx.fillStyle = colors[i % colors.length];
            ctx.fillRect(x, legendY - 4, 8, 8);
            ctx.fillStyle = getComputedStyle(document.documentElement).getPropertyValue('--text-secondary').trim() || '#666';
            ctx.textAlign = 'center';
            ctx.fillText(label.substring(0, 10), x + 4, legendY + 16);
        });
    }
}

function formatNum(n) {
    if (n >= 1000000) return (n / 1000000).toFixed(1) + 'M';
    if (n >= 1000) return (n / 1000).toFixed(1) + 'K';
    return Math.round(n).toString();
}
