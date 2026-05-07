// 1. Supabase Initialization (Correct URL & Publishable Key)
const SUPABASE_URL = 'https://ubnvjmvobwzsystdktpk.supabase.co';
const SUPABASE_KEY = 'sb_publishable_Fj_rv9LPpfh5nDouVW-bSw_hdfpn4-v';

const supabase = supabase.createClient(SUPABASE_URL, SUPABASE_KEY);

// Supabase Configuration
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
            
            submitBtn.innerText = "Processing...";
            submitBtn.disabled = true;

            // --- SIGNUP LOGIC ---
            const { data, error } = await supabase.auth.signUp({
                email: email,
                password: password
            });

            if (error) {
                alert("Signup Failed: " + error.message);
                submitBtn.innerText = "Sign Up";
                submitBtn.disabled = false;
            } else {
                alert("Account Created! Welcome to NexGenWebLab.");
                // Registration ke baad seedha tool par redirect
                window.location.href = "https://tools.nexgenweblab.com";
            }
        });
    }
});

// 2. Form Handling
document.addEventListener('DOMContentLoaded', () => {
    const authForm = document.getElementById('auth-form');
    
    if (authForm) {
        authForm.addEventListener('submit', async (e) => {
            e.preventDefault(); // Page refresh hone se roko
            
            const email = document.getElementById('email').value;
            const password = document.getElementById('password').value;
            const submitBtn = authForm.querySelector('button[type="submit"]');
            
            // Button ko loading state mein daalo
            submitBtn.innerText = "Creating Account...";
            submitBtn.disabled = true;

            // --- SIGNUP API CALL ---
            const { data, error } = await supabase.auth.signUp({
                email: email,
                password: password
            });

            if (error) {
                // Agar email pehle se use hui hai ya password chota hai
                alert("Error: " + error.message);
                submitBtn.innerText = "Sign Up";
                submitBtn.disabled = false;
            } else {
                // Account successfully ban gaya!
                alert("Account Created Successfully! Redirecting to Tool...");
                // Naya user seedha tool par redirect ho jayega
                window.location.href = "https://tools.nexgenweblab.com";
            }
        });
    }
});
