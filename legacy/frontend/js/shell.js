/* ═══════════════════════════════════════════════════════════
   BACK2ME  |  Shell builder  (injects topbar + sidebar)
   ═══════════════════════════════════════════════════════════ */

function buildShell(pageId, contentHTML) {
  document.body.innerHTML = `
<div class="app-shell">

  <!-- TOPBAR -->
  <header class="topbar">
    <a class="topbar-logo" href="/pages/home.html">
      <div class="logo-icon">📍</div>
      Back<span class="logo-2">2</span>Me
    </a>

    <nav class="topbar-nav">
      <a class="nav-link" href="/pages/home.html">
        Home
      </a>
      <a class="nav-link" href="/pages/lost.html">
        Lost
      </a>
      <a class="nav-link" href="/pages/found.html">
        Found
      </a>
      <a class="nav-link" href="/pages/search.html">
        Search
      </a>
    </nav>

    <div class="topbar-actions">
      <span class="text-muted text-sm" data-username></span>
      <a href="/pages/create-post.html" class="btn btn-primary btn-sm">+ New Post</a>
      <button id="logoutBtn" class="btn btn-ghost btn-sm">Sign out</button>
    </div>
  </header>

  <!-- SIDEBAR -->
  <aside class="sidebar">
    <span class="sidebar-section-label">Navigation</span>

    <a class="sidebar-item" href="/pages/home.html">
      Home
    </a>
    <a class="sidebar-item" href="/pages/lost.html">
      Lost Items
    </a>
    <a class="sidebar-item" href="/pages/found.html">
      Found Items
    </a>
    <a class="sidebar-item" href="/pages/search.html">
      Search
    </a>

    <div class="sidebar-divider"></div>
    <span class="sidebar-section-label">You</span>

    <a class="sidebar-item" href="/pages/create-post.html">
      <span class="sidebar-icon">✏️</span> Create Post
    </a>
    <a class="sidebar-item" href="/pages/messages.html">
      <span class="sidebar-icon">💬</span> Messages
    </a>
  </aside>

  <!-- MAIN CONTENT -->
  <main class="main-content" id="main-content">
    ${contentHTML}
  </main>

</div>`;

  // highlight active nav items
  const path = window.location.pathname;
  document.querySelectorAll('.sidebar-item, .nav-link').forEach(el => {
    const href = el.getAttribute('href') || '';
    if (href && path.endsWith(href.split('/').pop())) {
      el.classList.add('active');
    }
  });

  // logout
  document.getElementById('logoutBtn').addEventListener('click', e => {
    e.preventDefault();
    Auth.logout();
  });
}

/* helper: fill username placeholders after auth check */
function fillUser(user) {
  document.querySelectorAll('[data-username]').forEach(el => {
    el.textContent = user.username;
  });
}
