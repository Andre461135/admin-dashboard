(function() {
    'use strict';

    document.addEventListener('DOMContentLoaded', function() {

        setTimeout(function() {
            const overlay = document.getElementById('loadingOverlay');
            if (overlay) overlay.classList.remove('active');
        }, 300);

        initSidebar();
        initThemeToggle();
        initNotifications();
        initSmartSearch();
        initAlertDismiss();
        initStatAnimations();
    });

    /* ===================== Sidebar ===================== */
    function initSidebar() {
        const sidebar = document.getElementById('sidebar');
        const toggle = document.getElementById('sidebarToggle');
        const mobileBtn = document.getElementById('mobileMenuBtn');

        if (toggle && sidebar) {
            toggle.addEventListener('click', function() {
                sidebar.classList.toggle('collapsed');
            });
        }

        if (mobileBtn && sidebar) {
            mobileBtn.addEventListener('click', function() {
                sidebar.classList.toggle('mobile-open');
                let backdrop = document.querySelector('.sidebar-backdrop');
                if (!backdrop) {
                    backdrop = document.createElement('div');
                    backdrop.className = 'sidebar-backdrop';
                    backdrop.addEventListener('click', function() {
                        sidebar.classList.remove('mobile-open');
                        backdrop.classList.remove('active');
                    });
                    document.body.appendChild(backdrop);
                }
                backdrop.classList.toggle('active');
            });
        }
    }

    /* ===================== Theme Toggle ===================== */
    function initThemeToggle() {
        const toggle = document.getElementById('themeToggle');
        if (!toggle) return;

        toggle.addEventListener('click', function() {
            const html = document.documentElement;
            const current = html.getAttribute('data-theme');
            const next = current === 'dark' ? 'light' : 'dark';

            fetch('/settings/toggle-theme', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCSRFToken()
                },
                body: JSON.stringify({theme: next})
            }).then(function(r) { return r.json(); }).then(function(data) {
                if (data.status === 'ok') {
                    html.setAttribute('data-theme', data.theme);
                }
            }).catch(function() {
                html.setAttribute('data-theme', next);
            });
        });
    }

    /* ===================== Notifications ===================== */
    function initNotifications() {
        const btn = document.getElementById('notifBtn');
        const menu = document.getElementById('notifMenu');
        if (!btn || !menu) return;

        btn.addEventListener('click', function(e) {
            e.stopPropagation();
            menu.classList.toggle('active');
        });

        document.addEventListener('click', function() {
            menu.classList.remove('active');
        });

        menu.addEventListener('click', function(e) {
            e.stopPropagation();
        });
    }

    /* ===================== Smart Search ===================== */
    function initSmartSearch() {
        const input = document.getElementById('smartSearch');
        const results = document.getElementById('searchResults');
        if (!input || !results) return;

        var debounceTimer;

        input.addEventListener('input', function() {
            clearTimeout(debounceTimer);
            var query = this.value.trim();

            if (query.length < 2) {
                results.classList.remove('active');
                return;
            }

            debounceTimer = setTimeout(function() {
                fetch('/ai/search?q=' + encodeURIComponent(query))
                    .then(function(r) { return r.json(); })
                    .then(function(data) {
                        results.innerHTML = '';
                        var hasResults = false;

                        if (data.users && data.users.length > 0) {
                            hasResults = true;
                            var section = document.createElement('div');
                            section.className = 'search-result-section';
                            section.innerHTML = '<h4>Users</h4>';
                            data.users.forEach(function(u) {
                                section.innerHTML += '<div class="search-result-item" data-href="/users">' +
                                    '<i class="fas fa-user"></i><span>' + escapeHtml(u.username) + ' (' + escapeHtml(u.email) + ')</span></div>';
                            });
                            results.appendChild(section);
                        }

                        if (data.products && data.products.length > 0) {
                            hasResults = true;
                            var section = document.createElement('div');
                            section.className = 'search-result-section';
                            section.innerHTML = '<h4>Products</h4>';
                            data.products.forEach(function(p) {
                                section.innerHTML += '<div class="search-result-item" data-href="/products">' +
                                    '<i class="fas fa-box"></i><span>' + escapeHtml(p.name) + ' - $' + p.price.toFixed(2) + '</span></div>';
                            });
                            results.appendChild(section);
                        }

                        if (data.transactions && data.transactions.length > 0) {
                            hasResults = true;
                            var section = document.createElement('div');
                            section.className = 'search-result-section';
                            section.innerHTML = '<h4>Transactions</h4>';
                            data.transactions.forEach(function(t) {
                                section.innerHTML += '<div class="search-result-item" data-href="/">' +
                                    '<i class="fas fa-credit-card"></i><span>#' + t.id + ' - $' + t.amount.toFixed(2) + ' (' + t.status + ')</span></div>';
                            });
                            results.appendChild(section);
                        }

                        if (!hasResults) {
                            results.innerHTML = '<div class="search-result-section"><div class="search-result-item">' +
                                '<span style="color:var(--text-muted)">No results found</span></div></div>';
                        }

                        results.classList.add('active');

                        results.querySelectorAll('.search-result-item').forEach(function(item) {
                            item.addEventListener('click', function() {
                                var href = this.dataset.href;
                                if (href) window.location.href = href;
                            });
                        });
                    });
            }, 300);
        });

        document.addEventListener('click', function() {
            results.classList.remove('active');
        });

        input.addEventListener('focus', function() {
            if (this.value.trim().length >= 2 && results.children.length > 0) {
                results.classList.add('active');
            }
        });
    }

    /* ===================== Alert Dismiss ===================== */
    function initAlertDismiss() {
        document.querySelectorAll('.alert-close').forEach(function(btn) {
            btn.addEventListener('click', function() {
                var alert = this.closest('.alert');
                alert.style.opacity = '0';
                alert.style.transform = 'translateY(-10px)';
                setTimeout(function() { alert.remove(); }, 300);
            });
        });

        setTimeout(function() {
            document.querySelectorAll('.alert').forEach(function(alert) {
                alert.style.opacity = '0';
                alert.style.transform = 'translateY(-10px)';
                setTimeout(function() { alert.remove(); }, 300);
            });
        }, 5000);
    }

    /* ===================== Stat Animations ===================== */
    function initStatAnimations() {
        var observer = new IntersectionObserver(function(entries) {
            entries.forEach(function(entry) {
                if (entry.isIntersecting) {
                    entry.target.style.opacity = '1';
                }
            });
        }, { threshold: 0.1 });

        document.querySelectorAll('.stat-card').forEach(function(card) {
            observer.observe(card);
        });
    }

    /* ===================== Global Functions ===================== */
    window.refreshDashboard = function() {
        var overlay = document.getElementById('loadingOverlay');
        if (overlay) overlay.classList.add('active');
        setTimeout(function() {
            window.location.reload();
        }, 500);
    };

    function getCSRFToken() {
        var meta = document.querySelector('meta[name="csrf-token"]');
        if (meta) return meta.getAttribute('content');

        var input = document.querySelector('input[name="csrf_token"]');
        if (input) return input.value;

        var token = document.cookie.match(/csrf_token=([^;]+)/);
        return token ? token[1] : '';
    }

    function escapeHtml(text) {
        var div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

})();
