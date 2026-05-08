// Supabase Initialization
const SUPABASE_URL = 'https://ubnvjmvobwzsystdktpk.supabase.co';
const SUPABASE_KEY = 'sb_publishable_Fj_rv9LPpfh5nDouVW-bSw_hdfpn4-v';

const supabaseClient = window.supabase.createClient(SUPABASE_URL, SUPABASE_KEY);

document.addEventListener('DOMContentLoaded', () => {
    const authForm = document.getElementById('auth-form');
    const paymentForm = document.getElementById('payment-form');
    const googleBtn = document.getElementById('google-login-btn');
    
    const step1Container = document.getElementById('step-1-container');
    const step2Container = document.getElementById('step-2-container');
    const formTitle = document.getElementById('form-title');
    
    // Check URL parameters for Plan auto-selection from Pricing page
    const urlParams = new URLSearchParams(window.location.search);
    const planParam = urlParams.get('plan');
    if (planParam === 'pro') {
        document.getElementById('plan-pro').checked = true;
    }

    // Temporary storage for redirect parameters
    let userEmail = "";
    let userPwd = "";

    // --- STEP 1: CREATE ACCOUNT LOGIC ---
    if (authForm) {
        authForm.addEventListener('submit', async (e) => {
            e.preventDefault(); 
            
            userEmail = document.getElementById('email').value;
            userPwd = document.getElementById('password').value;
            const selectedPlan = document.querySelector('input[name="plan"]:checked').value;
            const submitBtn = authForm.querySelector('button[type="submit"]');
            
            submitBtn.innerText = "Processing...";
            submitBtn.disabled = true;

            // Sending Plan info to Supabase Metadata
            const { data, error } = await supabaseClient.auth.signUp({
                email: userEmail,
                password: userPwd,
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
                // Success - Check Plan Type
                if (selectedPlan === 'pro') {
                    // Hide Step 1, Show Step 2 (Payment Form)
                    step1Container.classList.add('hidden');
                    step2Container.classList.remove('hidden');
                    formTitle.innerText = "Complete Payment";
                } else {
                    // Free Plan - Direct Redirect to Tool
                    const redirectUrl = `https://tools.nexgenweblab.com/?em=${encodeURIComponent(userEmail)}&pw=${encodeURIComponent(userPwd)}`;
                    window.location.href = redirectUrl;
                }
            }
        });
    }

    // --- STEP 2: DUMMY PAYMENT LOGIC ---
    if (paymentForm) {
        paymentForm.addEventListener('submit', (e) => {
            e.preventDefault();
            const payBtn = document.getElementById('pay-btn');
            
            payBtn.innerHTML = '<i class="fa-solid fa-spinner fa-spin"></i> Processing...';
            payBtn.disabled = true;

            // Simulating a 1.5 second payment process
            setTimeout(() => {
                alert("Payment Successful! Welcome to Enterprise Pro.");
                // Redirect to Tool with login credentials
                const redirectUrl = `https://tools.nexgenweblab.com/?em=${encodeURIComponent(userEmail)}&pw=${encodeURIComponent(userPwd)}`;
                window.location.href = redirectUrl;
            }, 1500);
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
                    queryParams: { plan: selectedPlan }
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