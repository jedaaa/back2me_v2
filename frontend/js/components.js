/**
 * BACK2ME PREMIUM - UI Components
 */

import { formatDate } from './ui-utils.js';

export function renderPostCard(post, currentUserId) {
    const isOwner = post.user_id === currentUserId;
    const badgeClass = post.post_type === 'lost' ? 'badge-lost' : 'badge-found';
    const badgeText = post.post_type === 'lost' ? '🔴 Lost' : '🟢 Found';

    return `
    <article class="premium-card post-card" id="post-${post._id}">
      <header class="post-card-header">
        <div class="user-info">
          <div class="avatar-sm" style="background-image: url('https://ui-avatars.com/api/?name=${encodeURIComponent(post.username)}&background=1e293b&color=fff')"></div>
          <div class="meta">
            <span class="username">${post.username}</span>
            <span class="time">${formatDate(post.created_at)}</span>
          </div>
        </div>
        <span class="badge ${badgeClass}">${badgeText}</span>
      </header>

      <div class="post-content">
        <h3 class="item-name">${post.item_name}</h3>
        <p class="description">${post.description || 'No description provided.'}</p>
        ${post.location ? `<div class="location"><span class="icon">📍</span> ${post.location}</div>` : ''}
      </div>

      <footer class="post-actions">
        <button class="btn btn-ghost btn-sm" onclick="window.openMessage('${post.user_id}', '${post.username}')">
          <span>Message</span>
        </button>
        ${isOwner ? `
          <button class="btn btn-ghost btn-sm btn-danger" onclick="window.deletePost('${post._id}')">
            <span>Delete</span>
          </button>
        ` : ''}
      </footer>
    </article>
  `;
}

// Inject Post Card internal styles
if (!document.getElementById('b2m-component-styles')) {
    const style = document.createElement('style');
    style.id = 'b2m-component-styles';
    style.innerHTML = `
    .post-card { margin-bottom: 1.5rem; padding: 1.5rem; display: flex; flex-direction: column; gap: 1rem; }
    .post-card-header { display: flex; justify-content: space-between; align-items: center; }
    .user-info { display: flex; align-items: center; gap: 0.75rem; }
    .avatar-sm { width: 32px; height: 32px; border-radius: 50%; background-size: cover; border: 1px solid var(--glass-border); }
    .meta { display: flex; flex-direction: column; }
    .username { font-weight: 600; font-size: 0.9rem; }
    .time { font-size: 0.75rem; color: var(--text-muted); }
    .badge { padding: 0.25rem 0.75rem; border-radius: 20px; font-size: 0.7rem; font-weight: 700; text-transform: uppercase; background: rgba(255,255,255,0.05); }
    .badge-lost { color: #ef4444; border: 1px solid rgba(239, 68, 68, 0.3); }
    .badge-found { color: #10b981; border: 1px solid rgba(16, 185, 129, 0.3); }
    .item-name { font-size: 1.25rem; font-weight: 700; color: var(--text-white); }
    .description { color: var(--text-dim); font-size: 0.95rem; margin-top: 0.5rem; }
    .location { display: flex; align-items: center; gap: 0.5rem; margin-top: 0.5rem; font-size: 0.85rem; color: var(--accent-secondary); font-weight: 500; }
    .post-actions { display: flex; justify-content: flex-end; gap: 0.75rem; padding-top: 1rem; border-top: 1px solid var(--glass-border); }
    .btn-sm { padding: 0.5rem 1rem; font-size: 0.8rem; }
    .btn-danger:hover { color: #ef4444; border-color: rgba(239, 68, 68, 0.3); }
  `;
    document.head.appendChild(style);
}
