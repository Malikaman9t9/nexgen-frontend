// 1. Supabase Initialization
const SUPABASE_URL = 'https://ubnvjmvobwzsystdktpk.supabase.co';
const SUPABASE_KEY = 'sb_publishable_Fj_rv9LPpfh5nDouVW-bSw_hdfpn4-v';

const supabaseClient = window.supabase.createClient(SUPABASE_URL, SUPABASE_KEY);

document.addEventListener('DOMContentLoaded', () => {
    const authForm = document.getElementById('auth-form');
    const googleBtn = document.getElementById('google-login-btn');
    const paymentBox = document.getElementById('payment-box');
    const planRadios = document.querySelectorAll('input[name="plan"]');
    
    // Check URL parameters for Plan auto-selection
    const urlParams = new URLSearchParams(window.location.search);
    const planParam = urlParams.get('plan');
    
    if (planParam === 'pro') {
        document.getElementById('plan-pro').checked = true;
        paymentBox.classList.remove('hidden');
    }

    // Toggle dummy payment box on radio change
    planRadios.forEach(radio => {
        radio.addEventListener('change', (e) => {
            if (e.target.value === 'pro') {
                paymentBox.classList.remove('hidden');
            } else {
                paymentBox.classList.add('hidden');
            }
        });
    });

    // --- EMAIL SIGNUP WITH PLAN METADATA ---
    if (authForm) {
        authForm.addEventListener('submit', async (e) => {
            e.preventDefault(); 
            
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            const selectedPlan = document.querySelector('input[name="plan"]:checked').value;
            const submitBtn = authForm.querySelector('button[type="submit"]');
            
            submitBtn.innerText = "Processing...";
            submitBtn.disabled = true;

            // Sending Plan info to Supabase Metadata
            const { data, error } = await supabaseClient.auth.signUp({
                email: email,
                password: password,
                options: {
                    data: {
                        plan: selectedPlan
                    }
                }
            });

            if (error) {
                alert("Signup Error: " + error.message);
                submitBtn.innerText = "Create Account & Continue";
                submitBtn.disabled = false;
            } else {
                // Success - Redirecting to backend for auto-login
                const redirectUrl = `https://tools.nexgenweblab.com/?em=${encodeURIComponent(email)}&pw=${encodeURIComponent(password)}`;
                window.location.href = redirectUrl;
            }
        });
    }

    // --- GOOGLE OAUTH LOGIC ---
    if (googleBtn) {
        googleBtn.addEventListener('click', async () => {
            googleBtn.innerHTML = "Connecting...";
            googleBtn.disabled = true;

            const selectedPlan = document.querySelector('input[name="plan"]:checked').value;

            const { data, error } = await supabaseClient.auth.signInWithOAuth({
                provider: 'google',
                options: {
                    redirectTo: 'https://tools.nexgenweblab.com',
                    queryParams: {
                        // Passing metadata for google signup
                        plan: selectedPlan
                    }
                }
            });

            if (error) {
                alert("Google Login Error: " + error.message);
                googleBtn.innerHTML = `<i class="fa-brands fa-google text-red-500"></i> Continue with Google`;
                googleBtn.disabled = false;
            }
        });
    }
});