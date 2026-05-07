// 1. Supabase Initialization (Variable name fixed to avoid crash)
const SUPABASE_URL = 'https://ubnvjmvobwzsystdktpk.supabase.co';
const SUPABASE_KEY = 'sb_publishable_Fj_rv9LPpfh5nDouVW-bSw_hdfpn4-v';

const supabaseClient = supabase.createClient(SUPABASE_URL, SUPABASE_KEY);

document.addEventListener('DOMContentLoaded', () => {
    const authForm = document.getElementById('auth-form');
    const googleBtn = document.getElementById('google-login-btn');
    
    // --- EMAIL / PASSWORD SIGNUP LOGIC ---
    if (authForm) {
        authForm.addEventListener('submit', async (e) => {
            e.preventDefault(); 
            
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            const submitBtn = authForm.querySelector('button[type="submit"]');
            
            submitBtn.innerText = "Creating Account...";
            submitBtn.disabled = true;

            // Supabase Signup API Call
            const { data, error } = await supabaseClient.auth.signUp({
                email: email,
                password: password
            });

            if (error) {
                alert("Signup Error: " + error.message);
                submitBtn.innerText = "Create Account";
                submitBtn.disabled = false;
            } else {
                alert("Account Created Successfully! Redirecting to Portal...");
                
                // Details ko URL mein bhej kar backend par auto-login karna
                const redirectUrl = `https://tools.nexgenweblab.com/?em=${encodeURIComponent(email)}&pw=${encodeURIComponent(password)}`;
                window.location.href = redirectUrl;
            }
        });
    }

    // --- GOOGLE OAUTH LOGIC ---
    if (googleBtn) {
        googleBtn.addEventListener('click', async () => {
            googleBtn.innerHTML = "Connecting to Google...";
            googleBtn.disabled = true;

            const { data, error } = await supabaseClient.auth.signInWithOAuth({
                provider: 'google',
                options: {
                    redirectTo: 'https://tools.nexgenweblab.com'
                }
            });

            if (error) {
                alert("Google Login Error: " + error.message);
                googleBtn.innerHTML = `<i class="fa-brands fa-google text-red-500"></i> Google`;
                googleBtn.disabled = false;
            }
        });
    }
});