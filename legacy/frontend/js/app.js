/* ═══════════════════════════════════════════════════════════
   BACK2ME  |  Shared JS utilities + API client
   ═══════════════════════════════════════════════════════════ */

const API = '/api';

/* ─── low-level fetch wrapper ──────────────────────────────── */
async function apiFetch(path, options = {}) {
  const url = API + path;
  try {
    const res = await fetch(url, {
      headers: { 'Content-Type': 'application/json', ...(options.headers || {}) },
      credentials: 'include',
      ...options,
      body: options.body ? JSON.stringify(options.body) : undefined,
    });
    const data = await res.json().catch(() => ({}));
    if (!res.ok) {
      console.error(`[API Error] ${options.method || 'GET'} ${url} -> HTTP ${res.status}`, data);
      throw new Error(data.error || `HTTP ${res.status}`);
    }
    return data;
  } catch (err) {
    console.error(`[Fetch Failure] ${url}:`, err.message);
    throw err;
  }
}

/* ─── auth helpers ─────────────────────────────────────────── */
const Auth = {
  async me() {
    try { return await apiFetch('/me'); } catch { return null; }
  },
  async login(email, password) {
    return apiFetch('/login', { method: 'POST', body: { email, password } });
  },
  async register(username, email, password) {
    return apiFetch('/register', { method: 'POST', body: { username, email, password } });
  },
  async logout() {
    await apiFetch('/logout', { method: 'POST' });
    window.location.href = '/pages/login.html';
  },
  async forgotPassword(email) {
    return apiFetch('/forgot-password', { method: 'POST', body: { email } });
  },
};

/* ─── posts helpers ────────────────────────────────────────── */
const Posts = {
  getAll(page = 1) { return apiFetch(`/posts?page=${page}`); },
  getLost(page = 1) { return apiFetch(`/posts/lost?page=${page}`); },
  getFound(page = 1) { return apiFetch(`/posts/found?page=${page}`); },
  search(q, type, page) {
    const params = new URLSearchParams({ q, post_type: type || 'all', page: page || 1 });
    return apiFetch(`/posts/search?${params}`);
  },
  create(payload) { return apiFetch('/posts', { method: 'POST', body: payload }); },
  delete(id) { return apiFetch(`/posts/${id}`, { method: 'DELETE' }); },
};

/* ─── messages helpers ─────────────────────────────────────── */
const Messages = {
  conversations() { return apiFetch('/messages/conversations'); },
  thread(userId) { return apiFetch(`/messages/${userId}`); },
  send(receiverId, text) {
    return apiFetch('/messages', {
      method: 'POST',
      body: { receiver_id: receiverId, message_text: text },
    });
  },
};

/* ─── toast system ─────────────────────────────────────────── */
function initToasts() {
  if (document.getElementById('toast-container')) return;
  const el = document.createElement('div');
  el.id = 'toast-container';
  el.className = 'toast-container';
  document.body.appendChild(el);
}

function toast(message, type = 'info', duration = 3500) {
  const container = document.getElementById('toast-container');
  const t = document.createElement('div');
  t.className = `toast ${type}`;
  t.textContent = message;
  container.appendChild(t);
  setTimeout(() => {
    t.classList.add('fade-out');
    t.addEventListener('animationend', () => t.remove());
  }, duration);
}

/* ─── post card renderer ───────────────────────────────────── */
function renderPost(post, currentUserId) {
  const badgeClass = post.post_type === 'lost' ? 'badge-lost' : 'badge-found';
  const badgeText = post.post_type === 'lost' ? '🔴 Lost' : '🟢 Found';
  const created = post.created_at
    ? new Date(post.created_at).toLocaleString()
    : '';

  const imgHTML = post.image_url
    ? `<div class="post-image-wrap">
         <img class="post-image" src="${esc(post.image_url)}" alt="${esc(post.item_name)}"
              onerror="this.parentElement.style.display='none'">
       </div>`
    : '';

  const deleteBtn = currentUserId && post.user_id === currentUserId
    ? `<button class="btn btn-sm btn-danger" onclick="deletePost('${post._id}')">🗑 Delete</button>`
    : '';

  const avatar = post.profile_image || `https://ui-avatars.com/api/?name=${encodeURIComponent(post.username)}&background=6366f1&color=fff&size=64`;

  return `
<article class="post-card" id="post-${post._id}">
  <header class="post-card-header">
    <img class="post-avatar" src="${esc(avatar)}" alt="${esc(post.username)}">
    <div class="post-meta">
      <div class="post-username">${esc(post.username)}</div>
      <div class="post-time">${esc(created)}</div>
    </div>
    <span class="post-badge ${badgeClass}">${badgeText}</span>
  </header>

  ${imgHTML}

  <h3 class="post-item-name">${esc(post.item_name)}</h3>

  <div class="post-details">
    ${post.place ? `<span class="post-detail"><span class="detail-icon">📍</span>${esc(post.place)}</span>` : ''}
    ${post.location ? `<span class="post-detail"><span class="detail-icon">🏛</span>${esc(post.location)}</span>` : ''}
    ${post.time ? `<span class="post-detail"><span class="detail-icon">🕐</span>${esc(post.time)}</span>` : ''}
  </div>

  ${post.description ? `<p class="post-description">${esc(post.description)}</p>` : ''}

  <footer class="post-actions">
    ${deleteBtn}
    <button class="btn btn-sm btn-outline"
      onclick="openMessage('${post.user_id}','${esc(post.username)}')">
      💬 Message
    </button>
  </footer>
</article>`;
}

/* ─── helper: open message in messages page ────────────────── */
function openMessage(userId, username) {
  window.location.href = `/pages/messages.html?to=${userId}&name=${encodeURIComponent(username)}`;
}

/* ─── helper: delete post ──────────────────────────────────── */
async function deletePost(id) {
  if (!confirm('Delete this post?')) return;
  try {
    await Posts.delete(id);
    const el = document.getElementById(`post-${id}`);
    if (el) el.remove();
    toast('Post deleted', 'success');
  } catch (e) {
    toast(e.message, 'error');
  }
}

/* ─── escape HTML ─────────────────────────────────────────── */
function esc(str) {
  if (!str) return '';
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

/* ─── spinner helpers ─────────────────────────────────────── */
function showSpinner(containerId) {
  const el = document.getElementById(containerId);
  if (el) el.innerHTML = '<div class="spinner"></div>';
}

function showEmpty(containerId, title, text) {
  const el = document.getElementById(containerId);
  if (el) el.innerHTML = `
    <div class="empty-state">
      <div class="empty-icon">📭</div>
      <div class="empty-title">${title}</div>
      <p class="empty-text">${text}</p>
    </div>`;
}

/* ─── guard: redirect to login if not authenticated ───────── */
async function requireAuth() {
  const user = await Auth.me();
  if (!user) {
    console.warn('[Auth] No session found, redirecting to login.');
    window.location.href = '/pages/login.html';
    return null;
  }
  return user;
}

/* ─── guard: redirect home if already logged in ──────────── */
async function redirectIfLoggedIn() {
  const user = await Auth.me();
  if (user) window.location.href = '/pages/home.html';
}

/* ─── sidebar active link ─────────────────────────────────── */
function setSidebarActive() {
  const path = window.location.pathname;
  document.querySelectorAll('.sidebar-item, .nav-link').forEach(el => {
    const href = el.getAttribute('href') || '';
    if (href && path.includes(href.split('/').pop().replace('.html', ''))) {
      el.classList.add('active');
    }
  });
}

/* ─── populate topbar user info ───────────────────────────── */
function populateUserInfo(user) {
  document.querySelectorAll('[data-username]').forEach(el => {
    el.textContent = user.username;
  });
}

/* ─── init on DOM ready ───────────────────────────────────── */
document.addEventListener('DOMContentLoaded', () => {
  initToasts();
  setSidebarActive();

  const logoutBtn = document.getElementById('logoutBtn');
  if (logoutBtn) {
    logoutBtn.addEventListener('click', e => {
      e.preventDefault();
      Auth.logout();
    });
  }
});
