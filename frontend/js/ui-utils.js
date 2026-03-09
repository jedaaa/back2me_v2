/**
 * BACK2ME PREMIUM - UI Utilities
 * Shared components and formatting.
 */

/**
 * Toast Notification System
 * type: 'success' | 'error' | 'info'
 */
export function toast(message, type = 'info', duration = 4000) {
    let container = document.getElementById('b2m-toast-container');
    if (!container) {
        container = document.createElement('div');
        container.id = 'b2m-toast-container';
        container.style.cssText = `
      position: fixed;
      bottom: 2rem;
      right: 2rem;
      z-index: 9999;
      display: flex;
      flex-direction: column;
      gap: 0.75rem;
    `;
        document.body.appendChild(container);
    }

    const t = document.createElement('div');
    const bg = type === 'success' ? '#059669' : type === 'error' ? '#dc2626' : '#2563eb';

    t.style.cssText = `
    background: ${bg};
    color: white;
    padding: 1rem 1.5rem;
    border-radius: 12px;
    font-weight: 600;
    font-size: 0.9rem;
    box-shadow: 0 10px 15px -3px rgba(0,0,0,0.4);
    animation: slideIn 0.3s ease-out;
    min-width: 250px;
  `;
    t.textContent = message;

    container.appendChild(t);

    setTimeout(() => {
        t.style.opacity = '0';
        t.style.transform = 'translateY(10px)';
        t.style.transition = 'all 0.4s ease-out';
        setTimeout(() => t.remove(), 400);
    }, duration);
}

// Add CSS for toast animations if not present
if (!document.getElementById('b2m-toast-styles')) {
    const style = document.createElement('style');
    style.id = 'b2m-toast-styles';
    style.innerHTML = `
    @keyframes slideIn {
      from { opacity: 0; transform: translateX(30px); }
      to { opacity: 1; transform: translateX(0); }
    }
  `;
    document.head.appendChild(style);
}

/**
 * Format Date relative to now
 */
export function formatDate(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now - date;

    const mins = Math.floor(diff / 60000);
    const hours = Math.floor(mins / 60);
    const days = Math.floor(hours / 24);

    if (mins < 1) return 'Just now';
    if (mins < 60) return `${mins}m ago`;
    if (hours < 24) return `${hours}h ago`;
    if (days < 7) return `${days}d ago`;
    return date.toLocaleDateString();
}
