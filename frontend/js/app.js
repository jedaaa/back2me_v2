// frontend/js/app.js: Application Logic and Routing

// --- UTILS ---
function showToast(message, type = 'success') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <i class="fa-solid ${type === 'success' ? 'fa-check-circle' : 'fa-circle-exclamation'}"></i>
        <span>${message}</span>
    `;
    container.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}

function escapeHTML(str) {
    if (!str) return '';
    return str.replace(/[&<>'"]/g, tag => ({
        '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;'
    }[tag] || tag));
}

// --- ROUTING & VIEWS ---
const viewContainer = document.getElementById('view-container');
const navbar = document.getElementById('navbar');

const Views = {
    login: () => `
        <div class="glass glass-panel" style="max-width: 400px; margin: 2rem auto; animation: fadeUp 0.5s ease;">
            <div style="text-align: center; margin-bottom: 2rem;">
                <div style="font-size: 2rem; font-weight: 800; display: flex; align-items: center; justify-content: center; gap: 0.75rem; margin-bottom: 1rem; letter-spacing: -0.04em;">
                    <i class="fa-solid fa-rotate-left" style="color: var(--accent-primary); text-shadow: 0 0 10px var(--accent-glow);"></i>
                    <span>Back2Me</span>
                </div>
                <h2 class="text-gradient">Welcome Back</h2>
                <p style="color: var(--text-secondary)">Login to continue</p>
            </div>
            <form id="login-form">
                <div class="form-group">
                    <label class="form-label">Email Address</label>
                    <input type="email" id="log-email" class="form-control" required>
                </div>
                <div class="form-group">
                    <label class="form-label">Password</label>
                    <input type="password" id="log-password" class="form-control" required>
                </div>
                <button type="submit" class="btn btn-primary" style="width: 100%">Sign In</button>
            </form>
            <div style="text-align: center; margin-top: 1.5rem;">
                <a href="#register" style="color: var(--accent-primary); text-decoration: none;">Don't have an account? Register</a>
            </div>
        </div>
    `,

    register: () => `
        <div class="glass glass-panel" style="max-width: 400px; margin: 2rem auto; animation: fadeUp 0.5s ease;">
            <div style="text-align: center; margin-bottom: 2rem;">
                <div style="font-size: 2rem; font-weight: 800; display: flex; align-items: center; justify-content: center; gap: 0.75rem; margin-bottom: 1rem; letter-spacing: -0.04em;">
                    <i class="fa-solid fa-rotate-left" style="color: var(--accent-primary); text-shadow: 0 0 10px var(--accent-glow);"></i>
                    <span>Back2Me</span>
                </div>
                <h2 class="text-gradient">Create Account</h2>
                <p style="color: var(--text-secondary)">Join the community</p>
            </div>
            <form id="register-form">
                <div class="form-group">
                    <label class="form-label">Username</label>
                    <input type="text" id="reg-user" class="form-control" required>
                </div>
                <div class="form-group">
                    <label class="form-label">Email</label>
                    <input type="email" id="reg-email" class="form-control" required>
                </div>
                <div class="form-group">
                    <label class="form-label">Password</label>
                    <input type="password" id="reg-pass" class="form-control" required>
                </div>
                <button type="submit" class="btn btn-primary" style="width: 100%">Sign Up</button>
            </form>
            <div style="text-align: center; margin-top: 1.5rem;">
                <a href="#login" style="color: var(--accent-primary); text-decoration: none;">Already have an account? Login</a>
            </div>
        </div>
    `,

    lost: () => `
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem;">
            <h2><i class="fa-solid fa-search"></i> Lost <span class="text-gradient">Items</span></h2>
            <div style="display: flex; gap: 1rem;">
                <input type="text" id="lost-search" class="form-control" placeholder="Search lost items..." style="width: 250px;">
            </div>
        </div>
        <div id="lost-grid" class="grid grid-cols-2">
            <div class="spinner-container"><div class="spinner"></div></div>
        </div>
    `,

    found: () => `
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem;">
            <h2><i class="fa-solid fa-box-open"></i> Found <span class="text-gradient">Items</span></h2>
            <div style="display: flex; gap: 1rem;">
                <input type="text" id="found-search" class="form-control" placeholder="Search found items..." style="width: 250px;">
            </div>
        </div>
        <div id="found-grid" class="grid grid-cols-2">
            <div class="spinner-container"><div class="spinner"></div></div>
        </div>
    `,

    create: () => `
        <div class="glass glass-panel" style="max-width: 600px; margin: 0 auto;">
            <h2 class="text-gradient"><i class="fa-solid fa-plus"></i> Report Item</h2>
            <form id="create-post-form" style="margin-top: 1.5rem;">
                <div class="form-group">
                    <label class="form-label">Item Name</label>
                    <input type="text" id="post-title" class="form-control" required>
                </div>
                <div class="form-group">
                    <label class="form-label">Type</label>
                    <select id="post-type" class="form-control" required>
                        <option value="lost">I Lost This</option>
                        <option value="found">I Found This</option>
                    </select>
                </div>
                <div class="form-group">
                    <label class="form-label">Location (Where was it lost/found?)</label>
                    <input type="text" id="post-location" class="form-control" required>
                </div>
                <div class="form-group">
                    <label class="form-label">Description</label>
                    <textarea id="post-desc" class="form-control" rows="4" required></textarea>
                </div>
                <div class="form-group document-capture-group">
                    <label class="form-label">Image (Optional)</label>
                    <div style="display: flex; gap: 0.5rem; margin-bottom: 0.5rem;">
                        <button type="button" id="btn-upload-file" class="btn btn-dark" style="flex: 1;"><i class="fa-solid fa-upload"></i> Upload File</button>
                        <button type="button" id="btn-open-camera" class="btn btn-dark" style="flex: 1;"><i class="fa-solid fa-camera"></i> Open Camera</button>
                    </div>
                    
                    <input type="file" id="post-img-file" accept="image/*" style="display: none;">
                    
                    <!-- Camera Preview Area (Hidden initially) -->
                    <div id="camera-container" style="display: none; flex-direction: column; align-items: center; gap: 0.5rem; background: #000; border-radius: var(--radius-md); padding: 1rem; position: relative; margin-top: 1rem;">
                        <video id="camera-video" autoplay playsinline style="width: 100%; max-height: 400px; border-radius: var(--radius-sm); object-fit: cover;"></video>
                        <canvas id="camera-canvas" style="display: none;"></canvas>
                        <button type="button" id="btn-capture" class="btn btn-primary" style="position: absolute; bottom: 1.5rem;"><i class="fa-solid fa-camera"></i> Capture Photo</button>
                        <button type="button" id="btn-close-camera" class="btn btn-ghost" style="position: absolute; top: 0.5rem; right: 0.5rem; color: white; background: rgba(0,0,0,0.5); width: 32px; height: 32px; border-radius: 50%; padding: 0; display: flex; align-items: center; justify-content: center;"><i class="fa-solid fa-xmark"></i></button>
                    </div>

                    <!-- Image Preview Area -->
                    <div id="image-preview-container" style="display: none; margin-top: 1rem; position: relative; width: max-content;">
                        <img id="image-preview" style="max-height: 200px; border-radius: var(--radius-sm); border: 1px solid var(--surface-border);">
                        <button type="button" id="btn-remove-image" style="position: absolute; top: -10px; right: -10px; background: var(--danger); color: white; width: 28px; height: 28px; border-radius: 50%; border: none; cursor: pointer; display: flex; align-items: center; justify-content: center; box-shadow: 0 2px 5px rgba(0,0,0,0.5);"><i class="fa-solid fa-xmark"></i></button>
                    </div>
                </div>
                <button type="submit" class="btn btn-primary" style="width: 100%">Post Item</button>
            </form>
        </div>
    `,

    recent: () => `
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 2rem;">
            <h2><i class="fa-solid fa-clock-rotate-left"></i> Recent <span class="text-gradient">Posts</span></h2>
        </div>
        <div id="recent-grid" class="grid grid-cols-2">
            <div class="spinner-container"><div class="spinner"></div></div>
        </div>
    `,

    search: () => `
        <div style="display: flex; flex-direction: column; align-items: center; margin-bottom: 3rem; text-align: center;">
            <h2><i class="fa-solid fa-magnifying-glass"></i> Discover <span class="text-gradient">Items</span></h2>
            <p style="color: var(--text-secondary); margin-bottom: 1.5rem;">Search through all lost and found items in your community.</p>
            <div style="position: relative; width: 100%; max-width: 600px;">
                <input type="text" id="global-search-input" class="form-control" placeholder="Search by item name, location, or description..." style="padding: 1rem 1rem 1rem 3rem; font-size: 1.1rem; border-radius: 50px; box-shadow: 0 4px 20px rgba(0,0,0,0.05);">
                <i class="fa-solid fa-search" style="position: absolute; left: 1.2rem; top: 50%; transform: translateY(-50%); color: var(--text-secondary);"></i>
            </div>
            <div style="margin-top: 1rem; display: flex; gap: 1rem; justify-content: center;">
                <select id="global-search-type" class="form-control" style="width: auto; border-radius: 50px;">
                    <option value="">All Types</option>
                    <option value="lost">Lost Only</option>
                    <option value="found">Found Only</option>
                </select>
            </div>
        </div>
        
        <div id="search-results-grid" class="grid grid-cols-2">
             <div style="grid-column: 1/-1; text-align: center; color: var(--text-secondary); padding: 3rem;">
                <i class="fa-solid fa-cloud-sun text-gradient" style="font-size: 3rem; margin-bottom: 1rem; opacity: 0.5;"></i>
                <p>Start typing above to search the database.</p>
             </div>
        </div>
    `,

    profile: () => `
        <div class="glass glass-panel" style="max-width: 800px; margin: 0 auto;">
            <div style="display: flex; align-items: center; gap: 2rem; margin-bottom: 2rem; border-bottom: 1px solid var(--glass-border); padding-bottom: 2rem;">
                <div style="width: 100px; height: 100px; border-radius: 50%; background: var(--accent-gradient); display: flex; align-items: center; justify-content: center; font-size: 3rem; color: white;">
                    <i class="fa-solid fa-user"></i>
                </div>
                <div>
                    <h2 class="text-gradient" id="profile-username">Loading...</h2>
                    <p style="color: var(--text-secondary)" id="profile-email">Loading...</p>
                    <p style="color: var(--text-secondary); margin-top: 0.5rem;"><small>Member since: <span id="profile-date">...</span></small></p>
                </div>
            </div>
            
            <h3>Your <span class="text-gradient">Reported Items</span></h3>
            <div id="profile-posts-grid" class="grid grid-cols-2" style="margin-top: 1.5rem;">
                <div class="spinner-container"><div class="spinner"></div></div>
            </div>
        </div>
    `
};

// --- RENDERERS ---
async function renderPostList(gridId, type, searchVal) {
    const grid = document.getElementById(gridId);
    if (!grid) return;

    try {
        let data;
        const currentUserId = API.getUser()?.id;

        if (gridId === 'profile-posts-grid' && currentUserId) {
            // Override with profile specific fetch
            data = await API.request(`/posts/user/${currentUserId}`);
        } else {
            data = await API.getPosts(type, searchVal);
        }

        grid.innerHTML = '';

        if (!data || !data.posts || data.posts.length === 0) {
            grid.innerHTML = '<p style="color: var(--text-secondary); grid-column: 1/-1; text-align: center; padding: 3rem;">No items found.</p>';
            return;
        }


        data.posts.forEach(post => {
            const date = new Date(post.created_at).toLocaleDateString();
            const badgeClass = post.post_type === 'lost' ? 'badge-lost' : 'badge-found';
            const isResolved = post.status === 'resolved';
            const resolvedClass = isResolved ? 'resolved-content' : '';
            const actionVerb = post.post_type === 'lost' ? 'Found It!' : 'Handed Over!';

            grid.innerHTML += `
                <div class="glass post-card view-enter ${resolvedClass}">
                    ${post.image_url ? `<img src="${escapeHTML(post.image_url)}" class="post-img" loading="lazy" onerror="this.style.display='none'">` : ''}
                    <div class="post-body">
                        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 1rem;">
                            <div>
                                <span class="badge ${badgeClass}">${post.post_type.toUpperCase()}</span>
                                ${isResolved ? `<span class="badge badge-resolved" style="margin-left: 0.5rem;"><i class="fa-solid fa-check"></i> RESOLVED</span>` : ''}
                            </div>
                            <small style="color: var(--text-secondary)">${date}</small>
                        </div>
                        <h3>${escapeHTML(post.item_name)}</h3>
                        <p style="color: var(--text-secondary); margin-bottom: 1rem; font-size: 0.9rem;">
                            <i class="fa-solid fa-location-dot"></i> ${escapeHTML(post.location)}
                        </p>
                        <p style="margin-bottom: 1.5rem;">${escapeHTML(post.description)}</p>
                        
                        <div style="display: flex; justify-content: space-between; align-items: center; border-top: 1px solid var(--surface-border); padding-top: 1rem;">
                            <span style="font-weight: 500; color: var(--text-primary); font-size: 0.9rem;">
                                <i class="fa-solid fa-circle-user" style="color: var(--text-secondary)"></i> @${escapeHTML(post.username)}
                            </span>
                            
                            <div style="display: flex; gap: 0.5rem;">
                                ${post.user_id === currentUserId && !isResolved ?
                    `<button class="btn btn-success btn-resolve" data-pid="${post.id}" style="padding: 0.25rem 0.5rem; font-size: 0.8rem;">
                                        <i class="fa-solid fa-check"></i> Mark ${actionVerb}
                                    </button>`
                    : ''}
                                ${post.user_id === currentUserId ?
                    `<button class="btn btn-ghost btn-del" data-pid="${post.id}" style="padding: 0.25rem 0.5rem; font-size: 0.8rem;"><i class="fa-solid fa-trash"></i></button>`
                    : ''}
                            </div>
                        </div>
                        
                        <!-- Comments Section inside Card -->
                        <div class="comments-section" id="comments-${post.id}">
                            <div class="comments-list" id="clist-${post.id}">
                                <div style="text-align:center; padding: 1rem;"><i class="fa-solid fa-spinner fa-spin text-secondary"></i></div>
                            </div>
                            ${!isResolved ? `
                            <form class="comment-form" data-pid="${post.id}" style="display: flex; gap: 0.5rem; margin-top: 1rem;">
                                <input type="text" class="form-control comment-input" placeholder="Ask a question or reply..." required style="padding: 0.5rem; font-size: 0.85rem;">
                                <button type="submit" class="btn btn-secondary" style="padding: 0.5rem 0.75rem;"><i class="fa-solid fa-paper-plane"></i></button>
                            </form>
                            ` : '<p style="color: var(--text-secondary); font-size: 0.85rem; text-align: center; margin-top: 1rem;"><i>Comments are locked (Resolved)</i></p>'}
                        </div>
                    </div>
                </div>
            `;
        });

        // Trigger loading of comments for all these posts
        data.posts.forEach(p => loadCommentsForPost(p.id));

        // Attach Handlers via Event Delegation on the Grid to survive redraws
        grid.onclick = async (e) => {
            const resolveBtn = e.target.closest('.btn-resolve');
            const delBtn = e.target.closest('.btn-del');

            if (resolveBtn) {
                const pid = resolveBtn.dataset.pid;
                if (confirm("Are you sure you want to mark this item as resolved?")) {
                    try {
                        resolveBtn.disabled = true;
                        await API.resolvePost(pid);
                        showToast("Post marked as resolved!");
                        // Reload the current view
                        if (window.location.hash === '#lost') renderLost();
                        else if (window.location.hash === '#found') renderFound();
                        else if (window.location.hash === '#profile') renderProfilePosts();
                    } catch (err) {
                        showToast(err.message, 'error');
                        resolveBtn.disabled = false;
                    }
                }
            }

            if (delBtn) {
                const pid = delBtn.dataset.pid;
                if (confirm("Delete this post permanently?")) {
                    try {
                        delBtn.disabled = true;
                        await API.deletePost(pid);
                        showToast("Post deleted");
                        if (window.location.hash === '#lost') renderLost();
                        else if (window.location.hash === '#found') renderFound();
                        else if (window.location.hash === '#profile') renderProfilePosts();
                    } catch (err) {
                        showToast(err.message, 'error');
                        delBtn.disabled = false;
                    }
                }
            }
        };

        document.querySelectorAll(`#${gridId} .comment-form`).forEach(form => {
            form.addEventListener('submit', async (e) => {
                e.preventDefault();
                const pid = e.currentTarget.dataset.pid;
                const input = e.currentTarget.querySelector('.comment-input');
                const text = input.value;
                if (!text) return;

                try {
                    await API.addComment(pid, text);
                    input.value = '';
                    loadCommentsForPost(pid);
                } catch (err) {
                    showToast(err.message, 'error');
                }
            });
        });

    } catch (err) {
        grid.innerHTML = `<p class="toast error">Failed to load items: ${err.message}</p>`;
    }
}

async function loadCommentsForPost(postId) {
    const listEl = document.getElementById(`clist-${postId}`);
    if (!listEl) return;

    try {
        const data = await API.getComments(postId);

        if (data.comments.length === 0) {
            listEl.innerHTML = '<p style="color: var(--text-secondary); font-size: 0.85rem; text-align: center;">No comments yet.</p>';
            return;
        }

        listEl.innerHTML = data.comments.map(c => {
            const time = new Date(c.created_at).toLocaleDateString([], { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
            return `
                <div class="comment">
                    <div class="comment-header">
                        <span class="comment-author">@${escapeHTML(c.username)}</span>
                        <span class="comment-time">${time}</span>
                    </div>
                    <div class="comment-body">${escapeHTML(c.comment_text)}</div>
                </div>
            `;
        }).join('');

    } catch (err) {
        listEl.innerHTML = `<p style="color: var(--danger); font-size: 0.8rem;">Error loading comments.</p>`;
    }
}

function renderLost() {
    renderPostList('lost-grid', 'lost', document.getElementById('lost-search').value);
}

function renderFound() {
    renderPostList('found-grid', 'found', document.getElementById('found-search').value);
}

function renderRecent() {
    renderPostList('recent-grid', '', '');
}

function renderGlobalSearch() {
    const searchVal = document.getElementById('global-search-input').value;
    const typeVal = document.getElementById('global-search-type').value;

    if (!searchVal.trim()) {
        const grid = document.getElementById('search-results-grid');
        if (grid) {
            grid.innerHTML = `
             <div style="grid-column: 1/-1; text-align: center; color: var(--text-secondary); padding: 3rem;">
                <i class="fa-solid fa-cloud-sun text-gradient" style="font-size: 3rem; margin-bottom: 1rem; opacity: 0.5;"></i>
                <p>Start typing above to search the database.</p>
             </div>`;
        }
        return;
    }

    renderPostList('search-results-grid', typeVal, searchVal);
}

// --- ROUTER ---
const Router = {
    async navigate() {
        const hash = window.location.hash.slice(1) || 'recent';
        const isAuth = API.isLoggedIn();

        // Navigation Guards
        if (!isAuth && !['login', 'register'].includes(hash)) {
            window.location.hash = 'login';
            return;
        }
        if (isAuth && ['login', 'register'].includes(hash)) {
            window.location.hash = 'feed';
            return;
        }

        // Toggle UI
        navbar.classList.toggle('hidden', !isAuth);
        document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
        const activeLink = document.querySelector(`.nav-link[data-route="${hash}"]`);
        if (activeLink) activeLink.classList.add('active');

        // Render View
        if (Views[hash]) {
            viewContainer.innerHTML = Views[hash]();
            this.bindEvents(hash);
        } else {
            viewContainer.innerHTML = '<h2>404 - Not Found</h2>';
        }
    },

    bindEvents(route) {
        if (route === 'login') {
            document.getElementById('login-form').addEventListener('submit', async (e) => {
                e.preventDefault();
                const btn = e.target.querySelector('button');
                btn.disabled = true;
                btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i>';
                try {
                    const res = await API.login(
                        document.getElementById('log-email').value,
                        document.getElementById('log-password').value
                    );
                    API.setSession(res.token, res.user);
                    showToast('Welcome back!');
                    window.location.hash = 'feed';
                } catch (err) {
                    showToast(err.message, 'error');
                } finally { btn.disabled = false; btn.textContent = 'Sign In'; }
            });
        }

        else if (route === 'register') {
            document.getElementById('register-form').addEventListener('submit', async (e) => {
                e.preventDefault();
                const btn = e.target.querySelector('button');
                btn.disabled = true;
                btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i>';
                try {
                    const res = await API.register(
                        document.getElementById('reg-user').value,
                        document.getElementById('reg-email').value,
                        document.getElementById('reg-pass').value
                    );
                    API.setSession(res.token, res.user);
                    showToast('Account created!');
                    window.location.hash = 'feed';
                } catch (err) {
                    showToast(err.message, 'error');
                } finally { btn.disabled = false; btn.textContent = 'Sign Up'; }
            });
        }

        else if (route === 'lost') {
            renderLost();
            document.getElementById('lost-search').addEventListener('input', (e) => {
                clearTimeout(window.searchTimeout);
                window.searchTimeout = setTimeout(renderLost, 500);
            });
        }

        else if (route === 'found') {
            renderFound();
            document.getElementById('found-search').addEventListener('input', (e) => {
                clearTimeout(window.searchTimeout);
                window.searchTimeout = setTimeout(renderFound, 500);
            });
        }

        else if (route === 'recent') {
            renderRecent();
        }

        else if (route === 'search') {
            const searchInput = document.getElementById('global-search-input');
            const typeSelect = document.getElementById('global-search-type');

            searchInput.addEventListener('input', () => {
                clearTimeout(window.searchTimeout);
                window.searchTimeout = setTimeout(renderGlobalSearch, 500);
            });

            typeSelect.addEventListener('change', renderGlobalSearch);
        }

        else if (route === 'create') {
            let capturedFile = null;
            let currentStream = null;

            const fileInput = document.getElementById('post-img-file');
            const btnUpload = document.getElementById('btn-upload-file');
            const btnCamera = document.getElementById('btn-open-camera');
            const cameraContainer = document.getElementById('camera-container');
            const video = document.getElementById('camera-video');
            const canvas = document.getElementById('camera-canvas');
            const btnCapture = document.getElementById('btn-capture');
            const btnCloseCamera = document.getElementById('btn-close-camera');

            const previewContainer = document.getElementById('image-preview-container');
            const imagePreview = document.getElementById('image-preview');
            const btnRemoveImage = document.getElementById('btn-remove-image');

            // --- Handlers ---
            const stopCamera = () => {
                if (currentStream) {
                    currentStream.getTracks().forEach(track => track.stop());
                    currentStream = null;
                }
                cameraContainer.style.display = 'none';
            };

            const showPreview = (file) => {
                capturedFile = file;
                imagePreview.src = URL.createObjectURL(file);
                previewContainer.style.display = 'block';
                stopCamera();
            };

            const clearImage = () => {
                capturedFile = null;
                fileInput.value = '';
                previewContainer.style.display = 'none';
                imagePreview.src = '';
            };

            // 1. Upload File Button -> trigger hidden file input
            btnUpload.addEventListener('click', () => {
                fileInput.click();
            });

            fileInput.addEventListener('change', (e) => {
                if (e.target.files && e.target.files[0]) {
                    showPreview(e.target.files[0]);
                }
            });

            // 2. Open Camera
            btnCamera.addEventListener('click', async () => {
                clearImage();
                try {
                    currentStream = await navigator.mediaDevices.getUserMedia({
                        video: { facingMode: "environment" },
                        audio: false
                    });
                    video.srcObject = currentStream;
                    cameraContainer.style.display = 'flex';
                } catch (err) {
                    showToast('Failed to access camera: ' + err.message, 'error');
                }
            });

            // 3. Close Camera early
            btnCloseCamera.addEventListener('click', stopCamera);

            // 4. Capture Photo from Video stream
            btnCapture.addEventListener('click', () => {
                if (!currentStream) return;
                canvas.width = video.videoWidth;
                canvas.height = video.videoHeight;
                const ctx = canvas.getContext('2d');
                ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

                // Convert canvas to Blob -> File
                canvas.toBlob((blob) => {
                    const file = new File([blob], "camera_capture.jpg", { type: "image/jpeg" });
                    showPreview(file);
                    stopCamera();
                }, 'image/jpeg', 0.9);
            });

            // 5. Remove Image preview
            btnRemoveImage.addEventListener('click', clearImage);

            // Clean up camera on view unmount
            const cleanupOnNav = () => { stopCamera(); window.removeEventListener('hashchange', cleanupOnNav); };
            window.addEventListener('hashchange', cleanupOnNav);

            // 6. Form Submit
            document.getElementById('create-post-form').addEventListener('submit', async (e) => {
                e.preventDefault();
                const btn = e.target.querySelector('button[type="submit"]');
                btn.disabled = true;
                btn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Posting...';

                try {
                    let uploadedImageUrl = "";

                    if (capturedFile) {
                        const uploadResponse = await API.uploadImage(capturedFile);
                        uploadedImageUrl = uploadResponse.image_url;
                    }

                    await API.createPost({
                        item_name: document.getElementById('post-title').value,
                        post_type: document.getElementById('post-type').value,
                        location: document.getElementById('post-location').value,
                        description: document.getElementById('post-desc').value,
                        image_url: uploadedImageUrl
                    });
                    showToast('Item posted successfully!');

                    const pType = document.getElementById('post-type').value;
                    window.location.hash = pType === 'lost' ? 'lost' : 'found';
                } catch (err) {
                    showToast(err.message, 'error');
                } finally {
                    btn.disabled = false;
                    btn.textContent = 'Post Item';
                }
            });
        }



        else if (route === 'profile') {
            const user = API.getUser();
            if (user) {
                document.getElementById('profile-username').innerText = '@' + user.username;
                document.getElementById('profile-email').innerText = user.email;

                // Re-use renderPostList with a minor tweak by clearing and filtering inside
                renderPostList('profile-posts-grid', '', ''); // We'll redefine for profile strictly down below:

                // Fetch full profile data to get created_at date
                API.request('/me').then(res => {
                    const date = new Date(res.user.created_at).toLocaleDateString();
                    document.getElementById('profile-date').innerText = date;
                }).catch(err => console.error("Could not load full profile data"));
            }
        }
    }
};

// --- INIT ---
window.addEventListener('hashchange', () => Router.navigate());
window.addEventListener('auth-expired', () => {
    showToast('Session expired. Please login again.', 'error');
    window.location.hash = 'login';
});

document.getElementById('logout-btn').addEventListener('click', () => {
    API.clearSession();
    window.location.hash = 'login';
});

// Start router
Router.navigate();
