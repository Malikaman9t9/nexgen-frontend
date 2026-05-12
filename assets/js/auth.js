const SUPABASE_URL = 'https://ubnvjmvobwzsystdktpk.supabase.co';
const SUPABASE_KEY = 'sb_publishable_Fj_rv9LPpfh5nDouVW-bSw_hdfpn4-v';
const supabaseClient = window.supabase.createClient(SUPABASE_URL, SUPABASE_KEY);

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
                const plan = urlParams.get('plan') || 'free';
                if (plan === 'pro') {
                    window.location.href = `/upgrade`;
                } else {
                    window.location.href = `https://tools.nexgenweblab.com`;
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
                if (selectedPlan === 'pro') {
                    window.location.href = `/upgrade?access_token=${encodeURIComponent(accessToken)}&refresh_token=${encodeURIComponent(refreshToken)}`;
                } else {
                    window.location.href = `https://tools.nexgenweblab.com/?access_token=${encodeURIComponent(accessToken)}&refresh_token=${encodeURIComponent(refreshToken)}`;
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

            const { data, error } = await supabaseClient.auth.signInWithOAuth({
                provider: 'google',
                options: {
                    redirectTo: selectedPlan === 'pro'
                        ? 'https://nexgenweblab.com/upgrade'
                        : 'https://tools.nexgenweblab.com',
                    queryParams: { plan: selectedPlan }
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