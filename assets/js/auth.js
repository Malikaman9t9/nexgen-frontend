// 1. Supabase Initialization
const SUPABASE_URL = 'https://ubnvjmvobwzsystdktpk.supabase.co';
const SUPABASE_KEY = 'sb_publishable_Fj_rv9LPpfh5nDouVW-bSw_hdfpn4-v';

const supabase = supabase.createClient(SUPABASE_URL, SUPABASE_KEY);

document.addEventListener('DOMContentLoaded', () => {
    const authForm = document.getElementById('auth-form');
    
    if (authForm) {
        authForm.addEventListener('submit', async (e) => {
            e.preventDefault(); 
            
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            const submitBtn = authForm.querySelector('button[type="submit"]');
            
            submitBtn.innerText = "Creating Account...";
            submitBtn.disabled = true;

            // --- SIGNUP API CALL ---
            const { data, error } = await supabase.auth.signUp({
                email: email,
                password: password
            });

            if (error) {
                alert("Error: " + error.message);
                submitBtn.innerText = "Create Account";
                submitBtn.disabled = false;
            } else {
                alert("Account Created Successfully! Redirecting to Login...");
                
                // USER KI DETAILS KO BACKEND URL MEIN ATTACH KARNA
                const redirectUrl = `https://tools.nexgenweblab.com/?em=${encodeURIComponent(email)}&pw=${encodeURIComponent(password)}`;
                window.location.href = redirectUrl;
            }
        });
    }
});