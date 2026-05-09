const SUPABASE_URL = 'https://ubnvjmvobwzsystdktpk.supabase.co';
const SUPABASE_KEY = 'sb_publishable_Fj_rv9LPpfh5nDouVW-bSw_hdfpn4-v';
const supabaseClient = window.supabase.createClient(SUPABASE_URL, SUPABASE_KEY);

document.addEventListener('DOMContentLoaded', () => {
    const authForm = document.getElementById('auth-form');
    const googleBtn = document.getElementById('google-login-btn');
    
    // Auto-select plan from Pricing page link (e.g. /auth?plan=pro)
    const urlParams = new URLSearchParams(window.location.search);
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
                // REDIRECT LOGIC
                if (selectedPlan === 'pro') {
                    // Send to Upgrade page with details for auto-login after payment
                    window.location.href = `/upgrade?em=${encodeURIComponent(email)}&pw=${encodeURIComponent(password)}`;
                } else {
                    // Send directly to Tool
                    window.location.href = `https://tools.nexgenweblab.com/?em=${encodeURIComponent(email)}&pw=${encodeURIComponent(password)}`;
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
                    redirectTo: selectedPlan === 'pro' ? 'https://nexgenweblab.com/upgrade' : 'https://tools.nexgenweblab.com',
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