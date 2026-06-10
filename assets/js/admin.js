const SUPABASE_URL = 'https://ubnvjmvobwzsystdktpk.supabase.co';
const SUPABASE_KEY = 'sb_publishable_Fj_rv9LPpfh5nDouVW-bSw_hdfpn4-v';
const supabaseClient = window.supabase.createClient(SUPABASE_URL, SUPABASE_KEY);

let currentEditPostId = null;

document.addEventListener('DOMContentLoaded', async () => {
    const urlParams = new URLSearchParams(window.location.search);
    const authorized = urlParams.get('authorized');
    const authTimestamp = urlParams.get('t');

    if (authorized !== 'true' || !authTimestamp) {
        await supabaseClient.auth.signOut();
        window.location.href = '/auth.html?redirect=admin';
        return;
    }

    const elapsed = Date.now() - parseInt(authTimestamp);
    if (isNaN(elapsed) || elapsed > 300000) {
        await supabaseClient.auth.signOut();
        window.location.href = '/auth.html?redirect=admin';
        return;
    }

    const { data: { session } } = await supabaseClient.auth.getSession();
    if (!session) {
        window.location.href = '/auth.html?redirect=admin';
        return;
    }

    const { data: profile, error: profileError } = await supabaseClient
        .from('profiles')
        .select('role')
        .eq('id', session.user.id)
        .single();

    if (profileError || !profile || profile.role !== 'admin') {
        window.location.href = '/index.html';
        return;
    }

    history.replaceState(null, '', '/admin.html');
    initAdminDashboard();
});

function initAdminDashboard() {
    if (!document.getElementById('admin-dashboard')) return;

    const markdownInput = document.getElementById('markdown-input');
    const markdownPreview = document.getElementById('markdown-preview');
    const titleInput = document.getElementById('title-input');
    const featuredImageInput = document.getElementById('featured-image-input');
    const tagsInput = document.getElementById('tags-input');
    const statusSelect = document.getElementById('status-select');
    const savePostBtn = document.getElementById('save-post-btn');
    const postsListContainer = document.getElementById('posts-list');
    const tagsDisplay = document.getElementById('tags-display');
    const blogPostForm = document.getElementById('blog-post-form');

    if (markdownInput && markdownPreview) {
        markdownInput.addEventListener('input', () => {
            if (window.marked) {
                markdownPreview.innerHTML = window.marked.parse(markdownInput.value);
            } else {
                markdownPreview.textContent = markdownInput.value;
                markdownPreview.innerHTML = markdownPreview.textContent.replace(/\n/g, '<br>');
            }
        });
    }

    if (tagsInput && tagsDisplay) {
        const addTag = (tagText) => {
            const cleanTag = tagText.trim();
            if (!cleanTag) return;
            const el = document.createElement('span');
            el.className = 'inline-flex items-center gap-1.5 bg-primary/10 text-primary text-xs font-bold px-3 py-1.5 rounded-full';
            el.innerHTML = `${cleanTag} <button type="button" class="remove-tag hover:text-red-500 transition-colors"><i class="fa-solid fa-xmark"></i></button>`;
            el.querySelector('.remove-tag').addEventListener('click', () => { el.remove(); updateTagsInput(); });
            tagsDisplay.appendChild(el);
            updateTagsInput();
        };

        tagsInput.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' || e.key === ',') {
                e.preventDefault();
                addTag(tagsInput.value);
                tagsInput.value = '';
            }
        });

        tagsInput.addEventListener('paste', (e) => {
            e.preventDefault();
            const text = e.clipboardData.getData('text');
            text.split(',').forEach(t => addTag(t));
        });

        function updateTagsInput() {
            const tags = Array.from(tagsDisplay.querySelectorAll('span'))
                .map(el => el.childNodes[0].textContent.trim())
                .filter(t => t.length > 0);
            tagsInput.value = tags.join(', ');
        }
    }

    loadPosts();

    if (blogPostForm) {
        blogPostForm.addEventListener('submit', async (e) => {
            e.preventDefault();
            const title = titleInput.value.trim();
            const content = markdownInput ? markdownInput.value.trim() : '';
            const featuredImage = featuredImageInput.value.trim() || null;
            const tags = tagsInput.value.trim()
                .split(',')
                .map(tag => tag.trim())
                .filter(tag => tag.length > 0);
            const status = statusSelect.value;

            if (!title) { alert('Please enter a title'); return; }
            if (!content) { alert('Please enter content'); return; }

            savePostBtn.disabled = true;
            savePostBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Saving...';

            try {
                const { data: { session } } = await supabaseClient.auth.getSession();
                if (!session) throw new Error('No session');

                if (currentEditPostId) {
                    const { error } = await supabaseClient
                        .from('blog_posts')
                        .update({
                            title, content,
                            excerpt: content.substring(0, 150) + (content.length > 150 ? '...' : ''),
                            featured_image: featuredImage,
                            status, tags,
                            updated_at: new Date().toISOString()
                        })
                        .eq('id', currentEditPostId);
                    if (error) throw error;
                    currentEditPostId = null;
                } else {
                    const { error } = await supabaseClient
                        .from('blog_posts')
                        .insert({
                            title, content,
                            excerpt: content.substring(0, 150) + (content.length > 150 ? '...' : ''),
                            featured_image: featuredImage,
                            status, tags,
                            author_id: session.user.id
                        });
                    if (error) throw error;
                }

                titleInput.value = '';
                if (markdownInput) markdownInput.value = '';
                featuredImageInput.value = '';
                tagsInput.value = '';
                statusSelect.value = 'draft';
                if (markdownPreview) markdownPreview.innerHTML = '';
                if (tagsDisplay) tagsDisplay.innerHTML = '';
                loadPosts();
                savePostBtn.innerHTML = '<i class="fa-solid fa-cloud-upload-alt"></i> Save Post';
                savePostBtn.disabled = false;
            } catch (err) {
                console.error('Error saving post:', err);
                alert('Failed to save post: ' + err.message);
                savePostBtn.innerHTML = '<i class="fa-solid fa-cloud-upload-alt"></i> Save Post';
                savePostBtn.disabled = false;
            }
        });
    }
}

async function loadPosts() {
    const container = document.getElementById('posts-list');
    if (!container) return;

    try {
        const { data: posts, error } = await supabaseClient
            .from('blog_posts')
            .select('*')
            .order('created_at', { ascending: false });

        if (error) throw error;

        if (!posts || posts.length === 0) {
            container.innerHTML = `
                <div class="text-center py-12">
                    <div class="w-16 h-16 bg-slate-100 rounded-full flex items-center justify-center mx-auto mb-4">
                        <i class="fa-solid fa-newspaper text-slate-300 text-2xl"></i>
                    </div>
                    <p class="text-slate-500 font-bold">No posts yet. Create your first one!</p>
                </div>
            `;
            return;
        }

        container.innerHTML = '<div class="space-y-4"></div>';
        const list = container.querySelector('div');

        posts.forEach(post => {
            const date = new Date(post.created_at);
            const formattedDate = date.toLocaleDateString('en-US', {
                year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit'
            });

            const statusColors = {
                published: 'bg-emerald-100 text-emerald-700',
                draft: 'bg-amber-100 text-amber-700',
                archived: 'bg-red-100 text-red-700'
            };

            const statusColor = statusColors[post.status] || 'bg-slate-100 text-slate-600';

            const el = document.createElement('div');
            el.className = 'bg-slate-50 rounded-2xl p-5 border border-slate-200 hover:border-primary/20 transition-all';
            el.innerHTML = `
                <div class="flex items-start justify-between gap-4 mb-3">
                    <h3 class="font-black text-slate-900 text-base leading-snug">${post.title}</h3>
                    <span class="shrink-0 text-xs font-bold px-3 py-1 rounded-full ${statusColor}">${post.status}</span>
                </div>
                <p class="text-slate-500 text-sm font-medium mb-3 line-clamp-2">${post.excerpt || post.content.substring(0, 100) + '...'}</p>
                <div class="flex items-center justify-between">
                    <span class="text-xs text-slate-400 font-bold"><i class="far fa-calendar mr-1"></i>${formattedDate}</span>
                    <div class="flex gap-2">
                        <button class="btn-edit px-4 py-2 bg-white border border-slate-200 rounded-xl text-xs font-bold text-slate-600 hover:border-primary hover:text-primary transition-all" data-id="${post.id}">
                            <i class="fa-solid fa-pen"></i> Edit
                        </button>
                        <button class="btn-delete px-4 py-2 bg-white border border-slate-200 rounded-xl text-xs font-bold text-red-500 hover:border-red-300 hover:bg-red-50 transition-all" data-id="${post.id}">
                            <i class="fa-solid fa-trash-can"></i> Delete
                        </button>
                    </div>
                </div>
                ${post.tags && post.tags.length > 0 ? `
                <div class="flex flex-wrap gap-1.5 mt-3 pt-3 border-t border-slate-200">
                    ${post.tags.map(tag => `<span class="text-[10px] font-bold bg-primary/5 text-primary px-2 py-0.5 rounded-full">${tag}</span>`).join('')}
                </div>` : ''}
            `;
            list.appendChild(el);
        });

        container.querySelectorAll('.btn-edit').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const postId = e.currentTarget.getAttribute('data-id');
                editPost(postId);
            });
        });

        container.querySelectorAll('.btn-delete').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const postId = e.currentTarget.getAttribute('data-id');
                showDeleteModal(postId);
            });
        });
    } catch (err) {
        console.error('Error loading posts:', err);
        container.innerHTML = `<div class="text-center py-12"><p class="text-red-500 font-bold">Error loading posts: ${err.message}</p></div>`;
    }
}

async function editPost(postId) {
    try {
        const { data: post, error } = await supabaseClient
            .from('blog_posts')
            .select('*')
            .eq('id', postId)
            .single();

        if (error) throw error;

        document.getElementById('title-input').value = post.title;
        document.getElementById('markdown-input').value = post.content;
        document.getElementById('featured-image-input').value = post.featured_image || '';
        document.getElementById('status-select').value = post.status;

        if (post.tags && post.tags.length > 0) {
            document.getElementById('tags-input').value = post.tags.join(', ');
            const display = document.getElementById('tags-display');
            display.innerHTML = '';
            post.tags.forEach(tag => {
                const el = document.createElement('span');
                el.className = 'inline-flex items-center gap-1.5 bg-primary/10 text-primary text-xs font-bold px-3 py-1.5 rounded-full';
                el.innerHTML = `${tag} <button type="button" class="remove-tag hover:text-red-500 transition-colors"><i class="fa-solid fa-xmark"></i></button>`;
                el.querySelector('.remove-tag').addEventListener('click', () => { el.remove(); updateTagsInput(); });
                display.appendChild(el);
            });
        }

        if (window.marked) {
            document.getElementById('markdown-preview').innerHTML = window.marked.parse(post.content);
        }

        currentEditPostId = postId;
        document.getElementById('save-post-btn').innerHTML = '<i class="fa-solid fa-pen"></i> Update Post';
        window.scrollTo({ top: 0, behavior: 'smooth' });
    } catch (err) {
        console.error('Error editing post:', err);
        alert('Failed to load post for editing: ' + err.message);
    }
}

let pendingDeleteId = null;

function showDeleteModal(postId) {
    pendingDeleteId = postId;
    document.getElementById('delete-modal').classList.remove('hidden');
}

async function confirmDeletePost() {
    if (!pendingDeleteId) return;
    try {
        const { error } = await supabaseClient
            .from('blog_posts')
            .delete()
            .eq('id', pendingDeleteId);
        if (error) throw error;
        pendingDeleteId = null;
        document.getElementById('delete-modal').classList.add('hidden');
        loadPosts();
    } catch (err) {
        console.error('Error deleting post:', err);
        alert('Failed to delete post: ' + err.message);
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', async () => {
            try {
                await supabaseClient.auth.signOut();
                window.location.href = '/auth.html?redirect=admin';
            } catch (err) {
                console.error('Logout error:', err);
            }
        });
    }

    const cancelDelete = document.getElementById('cancel-delete');
    const confirmDelete = document.getElementById('confirm-delete');
    if (cancelDelete) cancelDelete.addEventListener('click', () => {
        document.getElementById('delete-modal').classList.add('hidden');
        pendingDeleteId = null;
    });
    if (confirmDelete) confirmDelete.addEventListener('click', confirmDeletePost);
    document.getElementById('delete-modal')?.addEventListener('click', (e) => {
        if (e.target === e.currentTarget) {
            document.getElementById('delete-modal').classList.add('hidden');
            pendingDeleteId = null;
        }
    });
});

function updateTagsInput() {
    const display = document.getElementById('tags-display');
    if (!display) return;
    const tags = Array.from(display.querySelectorAll('span'))
        .map(el => el.childNodes[0].textContent.trim())
        .filter(t => t.length > 0);
    document.getElementById('tags-input').value = tags.join(', ');
}
