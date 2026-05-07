// Apni Supabase Details Yahan Daalein
const SUPABASE_URL = 'https://ubnvjmvobwzsystdktpk.supabase.co';
const SUPABASE_KEY = 'sb_publishable_Fj_rv9LPpfh5nDouVW-bSw_hdfpn4-v';
const supabase = supabase.createClient(SUPABASE_URL, SUPABASE_KEY);

// Form element get kiya
const authForm = document.getElementById('auth-form');
const emailInput = document.getElementById('email');
const passwordInput = document.getElementById('password');

// Simple toggle for Login / Signup state
let isLoginMode = true; 
const submitBtn = authForm.querySelector('button[type="submit"]');
const toggleBtn = document.getElementById('toggle-auth'); // Hum auth.html mein ek id denge

authForm.addEventListener('submit', async function(e) {
    e.preventDefault();
    const email = emailInput.value;
    const password = passwordInput.value;
    
    submitBtn.innerText = "Processing...";

    if (isLoginMode) {
        // --- LOGIN LOGIC ---
        const { data, error } = await supabase.auth.signInWithPassword({ email, password });
        if (error) {
            alert("Login Failed: " + error.message);
            submitBtn.innerText = "Sign In";
        } else {
            alert("Login Successful! Redirecting to Tool...");
            // Redirect to Streamlit Tool
            window.location.href = "https://tools.nexgenweblab.com";
        }
    } else {
        // --- SIGNUP LOGIC ---
        const { data, error } = await supabase.auth.signUp({ email, password });
        if (error) {
            alert("Signup Failed: " + error.message);
            submitBtn.innerText = "Sign Up";
        } else {
            alert("Signup Successful! You can now log in.");
            isLoginMode = true; // Wapis login mode mein le aao
            submitBtn.innerText = "Sign In";
        }
    }
});