/**
 * BACK2ME PREMIUM - Shell Manager
 * Handles common UI layouts like Sidebar and Topbar.
 */

import { Auth } from './api.js';

export function buildShell(activePage, contentHtml) {
  const appContainer = document.createElement('div');
  appContainer.className = 'app-shell';

  appContainer.innerHTML = `
    <div class="fade-in">
        <!-- Top Navigation -->
        <header class="top-nav">
          <div class="top-nav-inner">
            <div class="logo gradient-text">Back2Me</div>
            <div class="user-profile">
              <span id="shell-username">...</span>
              <div class="avatar" id="shell-avatar"></div>
            </div>
          </div>
        </header>
    
        <div class="main-layout">
          <!-- Sidebar -->
          <aside class="sidebar premium-card">
            <nav class="sidebar-nav">
              <a href="home.html" class="sidebar-item ${activePage === 'home' ? 'active' : ''}">
                <span class="icon">📰</span> Feed
              </a>
              <a href="create-post.html" class="sidebar-item ${activePage === 'create' ? 'active' : ''}">
                <span class="icon">✨</span> Post
              </a>
              <a href="messages.html" class="sidebar-item ${activePage === 'messages' ? 'active' : ''}">
                <span class="icon">💬</span> Messages
              </a>
              <div class="spacer"></div>
              <button id="shell-logout" class="sidebar-item logout-btn">
                <span class="icon">➜</span> Logout
              </button>
            </nav>
          </aside>
    
          <!-- Main Content Area -->
          <main class="content-area">
            ${contentHtml}
          </main>
        </div>
    </div>
  `;

  document.body.innerHTML = '';
  document.body.appendChild(appContainer);

  // Handle Logout
  const logoutBtn = document.getElementById('shell-logout');
  if (logoutBtn) {
    logoutBtn.addEventListener('click', () => Auth.logout());
  }

  // Inject Shell Styles if not present
  _injectShellStyles();
}

export function fillUser(user) {
  const userEl = document.getElementById('shell-username');
  if (userEl) userEl.textContent = user.username;

  const avatarEl = document.getElementById('shell-avatar');
  if (avatarEl) {
    avatarEl.style.backgroundImage = `url('https://ui-avatars.com/api/?name=${encodeURIComponent(user.username)}&background=10b981&color=fff')`;
  }
}

function _injectShellStyles() {
  if (document.getElementById('b2m-shell-styles')) return;
  const style = document.createElement('style');
  style.id = 'b2m-shell-styles';
  style.innerHTML = `
    .app-shell { display: flex; flex-direction: column; min-height: 100vh; }
    .top-nav { height: 70px; border-bottom: 1px solid var(--glass-border); background: var(--glass-bg); backdrop-filter: blur(10px); position: sticky; top: 0; z-index: 100; }
    .top-nav-inner { max-width: 1400px; margin: 0 auto; height: 100%; display: flex; align-items: center; justify-content: space-between; padding: 0 2rem; }
    .main-layout { display: flex; flex: 1; max-width: 1400px; margin: 0 auto; width: 100%; padding: 2rem; gap: 2rem; }
    .sidebar { width: 280px; height: fit-content; position: sticky; top: 90px; padding: 1.5rem; }
    .sidebar-nav { display: flex; flex-direction: column; gap: 0.5rem; }
    .sidebar-item { display: flex; align-items: center; gap: 1rem; padding: 0.8rem 1.2rem; border-radius: 12px; color: var(--text-dim); text-decoration: none; transition: var(--ts-main); font-weight: 500; border: none; background: transparent; cursor: pointer; width: 100%; text-align: left; }
    .sidebar-item:hover { background: var(--glass-hover); color: var(--text-white); }
    .sidebar-item.active { background: var(--accent-glow); color: var(--accent-secondary); }
    .sidebar-item.logout-btn:hover { color: #ef4444; background: rgba(239, 68, 68, 0.1); }
    .avatar { width: 36px; height: 36px; border-radius: 50%; background-size: cover; border: 2px solid var(--accent-glow); }
    .user-profile { display: flex; align-items: center; gap: 0.75rem; font-weight: 600; font-size: 0.9rem; }
    .content-area { flex: 1; }
    .fade-in { animation: fadeIn 0.4s ease-out; }
    @keyframes fadeIn { from { opacity: 0; transform: translateY(5px); } to { opacity: 1; transform: translateY(0); } }
    .spacer { height: 2rem; }
  `;
  document.head.appendChild(style);
}
