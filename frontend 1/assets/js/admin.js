// Supabase client initialization (same as in auth.js)
const SUPABASE_URL = 'https://ubnvjmvobwzsystdktpk.supabase.co';
const SUPABASE_KEY = 'sb_publishable_Fj_rv9LPpfh5nDouVW-bSw_hdfpn4-v';
const supabaseClient = window.supabase.createClient(SUPABASE_URL, SUPABASE_KEY);

// Admin dashboard logic
document.addEventListener('DOMContentLoaded', async () => {
    // Check if user is logged in
    const { data: { session } } = await supabaseClient.auth.getSession();
    if (!session) {
        // No session, redirect to login
        window.location.href = '/auth.html';
        return;
    }

    // Fetch user's profile to check role
    const { data: profile, error: profileError } = await supabaseClient
        .from('profiles')
        .select('role')
        .eq('id', session.user.id)
        .single();

    if (profileError || !profile || profile.role !== 'admin') {
        // Not an admin, redirect to homepage
        window.location.href = '/index.html';
        return;
    }

    // User is admin, initialize the dashboard
    initAdminDashboard();
});

function initAdminDashboard() {
    // Check if we are on the admin dashboard page
    if (!document.getElementById('admin-dashboard')) {
        return; // Not on admin page
    }

    // Initialize markdown editor with preview
    const markdownInput = document.getElementById('markdown-input');
    const markdownPreview = document.getElementById('markdown-preview');
    const titleInput = document.getElementById('title-input');
    const featuredImageInput = document.getElementById('featured-image-input');
    const tagsInput = document.getElementById('tags-input');
    const statusSelect = document.getElementById('status-select');
    const savePostBtn = document.getElementById('save-post-btn');
    const postsListContainer = document.getElementById('posts-list');

    // Update preview as user types
    if (markdownInput && markdownPreview) {
        markdownInput.addEventListener('input', () => {
            // Use marked.js to render markdown (assuming it's loaded via CDN in admin.html)
            if (window.marked) {
                markdownPreview.innerHTML = window.marked.parse(markdownInput.value);
            } else {
                // Fallback: show plain text with line breaks
                markdownPreview.textContent = markdownInput.value;
                markdownPreview.innerHTML = markdownPreview.textContent.replace(/\n/g, '<br>');
            }
        });
    }

    // Load existing posts
    loadPosts();

    // Handle saving a post
    if (savePostBtn) {
        savePostBtn.addEventListener('click', async () => {
            const title = titleInput.value.trim();
            const content = markdownInput ? markdownInput.value.trim() : '';
            const featuredImage = featuredImageInput.value.trim() || null;
            const tags = tagsInput.value.trim()
                .split(',')
                .map(tag => tag.trim())
                .filter(tag => tag.length > 0);
            const status = statusSelect.value;

            // Validate
            if (!title) {
                alert('Please enter a title');
                return;
            }
            if (!content) {
                alert('Please enter content');
                return;
            }

            // Disable button during save
            savePostBtn.disabled = true;
            savePostBtn.textContent = 'Saving...';

            try {
                // Get the current user's session
                const { data: { session } } = await supabaseClient.auth.getSession();
                if (!session) throw new Error('No session');

                // Insert the new post
                const { data, error } = await supabaseClient
                    .from('blog_posts')
                    .insert({
                        title: title,
                        content: content,
                        excerpt: content.substring(0, 150) + (content.length > 150 ? '...' : ''),
                        featured_image: featuredImage,
                        status: status,
                        tags: tags,
                        author_id: session.user.id
                    });

                if (error) throw error;

                // Reset form
                titleInput.value = '';
                if (markdownInput) markdownInput.value = '';
                featuredImageInput.value = '';
                tagsInput.value = '';
                statusSelect.value = 'draft';
                if (markdownPreview) markdownPreview.innerHTML = '';

                // Reload posts list
                loadPosts();

                alert('Post saved successfully!');
            } catch (err) {
                console.error('Error saving post:', err);
                alert('Failed to save post: ' + err.message);
            } finally {
                savePostBtn.disabled = false;
                savePostBtn.textContent = 'Save Post';
            }
        });
    }
}

async function loadPosts() {
    const postsListContainer = document.getElementById('posts-list');
    if (!postsListContainer) return;

    try {
        const { data: posts, error } = await supabaseClient
            .from('blog_posts')
            .select('*')
            .order('created_at', { ascending: false });

        if (error) throw error;

        // Render posts list
        if (posts.length === 0) {
            postsListContainer.innerHTML = '<p>No posts found.</p>';
            return;
        }

        postsListContainer.innerHTML = '';
        posts.forEach(post => {
            const postElement = document.createElement('div');
            postElement.className = 'post-item';
            postElement.innerHTML = `
                <h3>${post.title}</h3>
                <p><strong>Status:</strong> <span class="status-${post.status}">${post.status}</span></p>
                <p><strong>Created:</strong> ${new Date(post.created_at).toLocaleString()}</p>
                <p>${post.excerpt || post.content.substring(0, 100) + '...'}</p>
                <div class="post-actions">
                    <button class="btn-edit" data-id="${post.id}">Edit</button>
                    <button class="btn-delete" data-id="${post.id}">Delete</button>
                </div>
                <hr>
            `;
            postsListContainer.appendChild(postElement);
        });

        // Add event listeners for edit/delete buttons
        document.querySelectorAll('.btn-edit').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                const postId = e.target.getAttribute('data-id');
                // TODO: Implement edit functionality
                alert('Edit functionality not implemented yet.');
            });
        });

        document.querySelectorAll('.btn-delete').forEach(btn => {
            btn.addEventListener('click', async (e) => {
                const postId = e.target.getAttribute('data-id');
                if (confirm('Are you sure you want to delete this post?')) {
                    try {
                        const { error } = await supabaseClient
                            .from('blog_posts')
                            .delete()
                            .eq('id', postId);

                        if (error) throw error;
                        loadPosts(); // Reload the list
                        alert('Post deleted successfully.');
                    } catch (err) {
                        console.error('Error deleting post:', err);
                        alert('Failed to delete post: ' + err.message);
                    }
                }
            });
        });
    } catch (err) {
        console.error('Error loading posts:', err);
        postsListContainer.innerHTML = `<p>Error loading posts: ${err.message}</p>`;
    }
}