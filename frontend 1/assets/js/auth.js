const SUPABASE_URL = 'https://ubnvjmvobwzsystdktpk.supabase.co';
const SUPABASE_KEY = 'sb_publishable_Fj_rv9LPpfh5nDouVW-bSw_hdfpn4-v';
const supabaseClient = window.supabase.createClient(SUPABASE_URL, SUPABASE_KEY);

// Form validation functions
function validateEmail(input) {
    const error = document.getElementById('email-error');
    if (input.value && !input.validity.valid) {
        error.classList.remove('hidden');
    } else {
        error.classList.add('hidden');
    }
}

function validatePassword(input) {
    const error = document.getElementById('password-error');
    if (input.value && input.value.length < 6) {
        error.classList.remove('hidden');
    } else {
        error.classList.add('hidden');
    }
}

document.addEventListener('DOMContentLoaded', async () => {
    const authForm = document.getElementById('auth-form');
    const googleBtn = document.getElementById('google-login-btn');
    const urlParams = new URLSearchParams(window.location.search);
    
    // Restore session from URL tokens (flow: auth → tools/upgrade)
    const accessToken = urlParams.get('access_token');
    const refreshToken = urlParams.get('refresh_token');
    if (accessToken && refreshToken) {
        try {
            await supabaseClient.auth.setSession({
                access_token: accessToken,
                refresh_token: refreshToken
            });
            const { data: { user } } = await supabaseClient.auth.getUser();
            if (user) {
                const plan = sessionStorage.getItem('selectedPlan') || 'free';
                sessionStorage.removeItem('selectedPlan');
                if (plan === 'pro') {
                    window.location.href = `/upgrade`;
                } else {
                    window.location.href = `https://dashboard.nexgenweblab.com`;
                }
                return;
            }
        } catch (e) {
        }
    }

    // Auto-select plan from URL (e.g. /auth?plan=pro)
    const planParam = urlParams.get('plan');
    if (planParam === 'pro' && document.getElementById('plan-pro')) {
        document.getElementById('plan-pro').checked = true;
    }

    if (authForm) {
        authForm.addEventListener('submit', async (e) => {
            e.preventDefault(); 
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            const selectedPlan = document.querySelector('input[name="plan"]:checked').value;
            const submitBtn = authForm.querySelector('button[type="submit"]');
            
            // Validate form
            if (!email || !email.includes('@')) {
                alert("Please enter a valid email address");
                return;
            }
            if (!password || password.length < 6) {
                alert("Password must be at least 6 characters");
                return;
            }
            
            submitBtn.innerText = "Processing...";
            submitBtn.disabled = true;

            // Save plan metadata to Supabase
            const { data, error } = await supabaseClient.auth.signUp({
                email: email,
                password: password,
                options: { data: { plan: selectedPlan } }
            });

            if (error) {
                alert("Signup Error: " + error.message);
                submitBtn.innerText = "Create Account";
                submitBtn.disabled = false;
            } else {
                const session = data.session;
                const accessToken = session?.access_token || '';
                const refreshToken = session?.refresh_token || '';
                if (session) {
                    await supabaseClient.auth.setSession({
                        access_token: accessToken,
                        refresh_token: refreshToken
                    });
                }
                // Store plan in session storage for redirect
                sessionStorage.setItem('selectedPlan', selectedPlan);
                if (selectedPlan === 'pro') {
                    window.location.href = `/upgrade`;
                } else {
                    window.location.href = `https://dashboard.nexgenweblab.com`;
                }
            }
        });
    }

    if (googleBtn) {
        googleBtn.addEventListener('click', async () => {
            googleBtn.innerHTML = "Connecting...";
            googleBtn.disabled = true;
            
            const planEl = document.querySelector('input[name="plan"]:checked');
            const selectedPlan = planEl ? planEl.value : 'free';

            // Store plan in session storage
            sessionStorage.setItem('selectedPlan', selectedPlan);

            const { data, error } = await supabaseClient.auth.signInWithOAuth({
                provider: 'google',
                options: {
                    redirectTo: selectedPlan === 'pro'
                        ? window.location.origin + '/upgrade'
                        : 'https://dashboard.nexgenweblab.com'
                }
            });

            if (error) {
                alert("Google Error: " + error.message);
                googleBtn.innerHTML = `<i class="fa-brands fa-google text-red-500"></i> Continue with Google`;
                googleBtn.disabled = false;
            }
        });
    }
});