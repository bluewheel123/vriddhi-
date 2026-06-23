// Vriddhi 2.0 - Unified Dynamic Authentication Engine (HTML/CSS/JS)
// Mirroring the gorgeous glassmorphism layout of modern-stunning-sign-in

document.addEventListener('DOMContentLoaded', () => {
    // 1. Inject the Auth Modal HTML into the DOM dynamically
    const modalContainer = document.createElement('div');
    modalContainer.innerHTML = `
    <!-- Modern Stunning Sign In / Sign Up Modal -->
    <div id="auth-modal" class="fixed inset-0 z-[9999] flex items-center justify-center bg-black/60 backdrop-blur-md hidden" style="font-family: 'Poppins', sans-serif;">
      <div class="relative w-full max-w-sm mx-4 rounded-3xl bg-gradient-to-br from-slate-900/90 to-slate-950/95 border border-white/10 shadow-2xl p-8 flex flex-col items-center">
        <!-- Close button -->
        <button onclick="closeLoginModal()" class="absolute top-5 right-5 text-white/40 hover:text-white transition-colors">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2">
            <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>

        <!-- Logo -->
        <div class="flex items-center justify-center w-12 h-12 rounded-full bg-white/10 mb-4 shadow-lg border border-white/10 transition-transform duration-300 hover:rotate-12 cursor-pointer">
          <img src="/logo.png" alt="Vriddhi Logo" class="w-8 h-8 object-contain rounded-full" />
        </div>

        <!-- Title -->
        <h2 class="text-xl font-bold text-white mb-6 text-center tracking-tight">
          Vriddhi 2.0 Login
        </h2>

        <!-- Form Switch Tabs -->
        <div class="flex w-full bg-white/5 p-1 rounded-xl mb-6 border border-white/5">
          <button id="tab-login" onclick="switchAuthTab('login')" class="flex-1 text-center py-2 text-xs font-bold rounded-lg transition-all bg-white/15 text-white">
            Sign In
          </button>
          <button id="tab-register" onclick="switchAuthTab('register')" class="flex-1 text-center py-2 text-xs font-bold rounded-lg transition-all text-white/60 hover:text-white">
            Register
          </button>
        </div>

        <!-- Error message -->
        <div id="auth-error" class="w-full text-xs text-red-400 mb-4 text-center hidden bg-red-500/10 border border-red-500/20 py-2.5 px-3 rounded-xl"></div>

        <!-- Inputs Container -->
        <div class="flex flex-col w-full gap-3 mb-6">
          <!-- Full Name (Register only) -->
          <div id="auth-name-container" class="hidden">
            <input
              id="auth-name"
              placeholder="Full Name"
              type="text"
              class="w-full px-5 py-3 rounded-xl bg-white/5 border border-white/10 text-white placeholder-gray-400 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition-all outline-none"
            />
          </div>

          <!-- Phone Number (Register only) -->
          <div id="auth-phone-container" class="hidden">
            <input
              id="auth-phone"
              placeholder="Phone Number"
              type="tel"
              class="w-full px-5 py-3 rounded-xl bg-white/5 border border-white/10 text-white placeholder-gray-400 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition-all outline-none"
            />
          </div>

          <!-- Email (Both) -->
          <div>
            <input
              id="auth-email"
              placeholder="Email Address"
              type="email"
              class="w-full px-5 py-3 rounded-xl bg-white/5 border border-white/10 text-white placeholder-gray-400 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition-all outline-none"
            />
          </div>

          <!-- Address (Register only) -->
          <div id="auth-address-container" class="hidden">
            <input
              id="auth-address"
              placeholder="Address (e.g. Kamrup, Assam)"
              type="text"
              class="w-full px-5 py-3 rounded-xl bg-white/5 border border-white/10 text-white placeholder-gray-400 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition-all outline-none"
            />
          </div>

          <!-- Password (Both) -->
          <div>
            <input
              id="auth-password"
              placeholder="Password"
              type="password"
              class="w-full px-5 py-3 rounded-xl bg-white/5 border border-white/10 text-white placeholder-gray-400 text-sm focus:outline-none focus:ring-2 focus:ring-emerald-500 focus:border-transparent transition-all outline-none"
            />
          </div>
        </div>

        <!-- Action Button -->
        <button
          id="auth-submit-btn"
          onclick="handleAuthSubmit()"
          class="w-full bg-emerald-600 hover:bg-emerald-500 text-white font-semibold py-3 rounded-xl shadow-lg transition-all active:scale-[0.98] text-sm flex items-center justify-center gap-2"
        >
          <span id="auth-btn-text">Sign In</span>
        </button>

        <!-- Google Sign In Demo -->
        <button onclick="alert('Google Sign-In is a demo feature. Please use regular register/login options.')" class="w-full mt-3 flex items-center justify-center gap-2 bg-gradient-to-b from-[#232526] to-[#2d2e30] border border-white/5 rounded-xl py-3 font-semibold text-white shadow hover:brightness-110 transition active:scale-[0.98] text-sm">
          <img
            src="https://www.svgrepo.com/show/475656/google-color.svg"
            alt="Google"
            class="w-5 h-5"
          />
          Continue with Google
        </button>

        <div class="w-full text-center mt-6">
          <span class="text-xs text-gray-400" id="auth-switch-prompt">
            Don't have an account? 
            <a href="#" onclick="switchAuthTab('register'); event.preventDefault();" class="underline text-emerald-400 hover:text-emerald-300 font-semibold">
              Sign up, it's free!
            </a>
          </span>
        </div>
      </div>
    </div>
    `;
    document.body.appendChild(modalContainer);

    // Initialize UI Auth triggers
    updateAuthUI();

    // Prefill user coordinates/area/profile if applicable
    prefillInsuranceForm();

    // Auto prompt login if requested via redirect URL params
    const urlParams = new URLSearchParams(window.location.search);
    if (urlParams.get('prompt_login') === 'true') {
        openLoginModal();
    }
});

// Global state tracking
let currentAuthTab = 'login';

function openLoginModal() {
    const modal = document.getElementById('auth-modal');
    if (modal) modal.classList.remove('hidden');
    
    const errorDiv = document.getElementById('auth-error');
    if (errorDiv) errorDiv.classList.add('hidden');
}

function closeLoginModal() {
    const modal = document.getElementById('auth-modal');
    if (modal) modal.classList.add('hidden');
}

function switchAuthTab(tab) {
    currentAuthTab = tab;
    const tabLogin = document.getElementById('tab-login');
    const tabRegister = document.getElementById('tab-register');
    const nameCont = document.getElementById('auth-name-container');
    const phoneCont = document.getElementById('auth-phone-container');
    const addrCont = document.getElementById('auth-address-container');
    const btnText = document.getElementById('auth-btn-text');
    const prompt = document.getElementById('auth-switch-prompt');
    const errDiv = document.getElementById('auth-error');

    if (errDiv) errDiv.classList.add('hidden');

    if (tab === 'login') {
        if (tabLogin) tabLogin.className = "flex-1 text-center py-2 text-xs font-bold rounded-lg transition-all bg-white/15 text-white";
        if (tabRegister) tabRegister.className = "flex-1 text-center py-2 text-xs font-bold rounded-lg transition-all text-white/60 hover:text-white";
        if (nameCont) nameCont.classList.add('hidden');
        if (phoneCont) phoneCont.classList.add('hidden');
        if (addrCont) addrCont.classList.add('hidden');
        if (btnText) btnText.innerText = "Sign In";
        if (prompt) prompt.innerHTML = `Don't have an account? <a href="#" onclick="switchAuthTab('register'); event.preventDefault();" class="underline text-emerald-400 hover:text-emerald-300 font-semibold">Sign up, it's free!</a>`;
    } else {
        if (tabLogin) tabLogin.className = "flex-1 text-center py-2 text-xs font-bold rounded-lg transition-all text-white/60 hover:text-white";
        if (tabRegister) tabRegister.className = "flex-1 text-center py-2 text-xs font-bold rounded-lg transition-all bg-white/15 text-white";
        if (nameCont) nameCont.classList.remove('hidden');
        if (phoneCont) phoneCont.classList.remove('hidden');
        if (addrCont) addrCont.classList.remove('hidden');
        if (btnText) btnText.innerText = "Create Account";
        if (prompt) prompt.innerHTML = `Already have an account? <a href="#" onclick="switchAuthTab('login'); event.preventDefault();" class="underline text-emerald-400 hover:text-emerald-300 font-semibold">Sign in here</a>`;
    }
}

function handleAuthSubmit() {
    const errDiv = document.getElementById('auth-error');
    if (errDiv) errDiv.classList.add('hidden');

    const email = document.getElementById('auth-email').value.trim();
    const password = document.getElementById('auth-password').value.trim();

    if (!email || !password) {
        if (errDiv) {
            errDiv.innerText = "Please fill in email and password fields.";
            errDiv.classList.remove('hidden');
        }
        return;
    }

    if (currentAuthTab === 'login') {
        fetch('/api/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password })
        })
        .then(res => res.json())
        .then(data => {
            if (data.status === 'success') {
                localStorage.setItem('logged_in_user', JSON.stringify(data.user));
                closeLoginModal();
                updateAuthUI();
                prefillInsuranceForm();
                alert("Login successful!");
                window.location.reload();
            } else {
                if (errDiv) {
                    errDiv.innerText = data.message;
                    errDiv.classList.remove('hidden');
                }
            }
        })
        .catch(err => {
            console.error("Login error:", err);
            if (errDiv) {
                errDiv.innerText = "Failed to connect to authentication server.";
                errDiv.classList.remove('hidden');
            }
        });
    } else {
        const name = document.getElementById('auth-name').value.trim();
        const phone = document.getElementById('auth-phone').value.trim();
        const address = document.getElementById('auth-address').value.trim();

        if (!name || !phone || !address) {
            if (errDiv) {
                errDiv.innerText = "All fields are required to register.";
                errDiv.classList.remove('hidden');
            }
            return;
        }

        fetch('/api/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, phone, email, address, password })
        })
        .then(res => res.json())
        .then(data => {
            if (data.status === 'success') {
                localStorage.setItem('logged_in_user', JSON.stringify(data.user));
                closeLoginModal();
                updateAuthUI();
                prefillInsuranceForm();
                alert("Registration successful! Welcome to Vriddhi.");
                window.location.reload();
            } else {
                if (errDiv) {
                    errDiv.innerText = data.message;
                    errDiv.classList.remove('hidden');
                }
            }
        })
        .catch(err => {
            console.error("Registration error:", err);
            if (errDiv) {
                errDiv.innerText = "Failed to connect to authentication server.";
                errDiv.classList.remove('hidden');
            }
        });
    }
}

function handleLogout() {
    fetch('/api/logout', { method: 'POST' })
    .then(() => {
        localStorage.removeItem('logged_in_user');
        updateAuthUI();
        prefillInsuranceForm();
        alert("Logged out successfully.");
        window.location.href = "/";
    })
    .catch(err => {
        console.error("Logout error:", err);
        localStorage.removeItem('logged_in_user');
        window.location.href = "/";
    });
}

function updateAuthUI() {
    const loggedInUser = JSON.parse(localStorage.getItem('logged_in_user'));
    
    // Dynamic navbar button triggers
    const loginBtns = document.querySelectorAll('#nav-login-btn');
    loginBtns.forEach(btn => {
        if (loggedInUser) {
            btn.innerText = 'Log Out';
            btn.style.pointerEvents = 'auto';
            btn.onclick = (e) => { e.preventDefault(); handleLogout(); };
        } else {
            btn.innerText = 'Log In';
            btn.style.pointerEvents = 'auto';
            btn.onclick = (e) => { e.preventDefault(); openLoginModal(); };
        }
    });

    const mobileLoginBtn = document.getElementById('nav-login-mobile-btn');
    if (mobileLoginBtn) {
        if (loggedInUser) {
            mobileLoginBtn.innerText = 'Log Out';
            mobileLoginBtn.onclick = () => { handleLogout(); if (typeof toggleMobileMenu === 'function') toggleMobileMenu(false); };
        } else {
            mobileLoginBtn.innerText = 'Log In';
            mobileLoginBtn.onclick = () => { openLoginModal(); if (typeof toggleMobileMenu === 'function') toggleMobileMenu(false); };
        }
    }
}

function prefillInsuranceForm() {
    const loggedInUser = JSON.parse(localStorage.getItem('logged_in_user'));
    const farmerIdInput = document.querySelector('input[name="farmer_id"]');
    const farmerNameInput = document.querySelector('input[name="farmer_name"]');
    const farmerEmailInput = document.getElementById('farmer-email');
    const farmerPhoneInput = document.getElementById('farmer-phone');
    const farmerAddressInput = document.getElementById('farmer-address');

    if (farmerIdInput && farmerNameInput) {
        if (loggedInUser) {
            farmerIdInput.value = loggedInUser.farmer_id;
            farmerNameInput.value = loggedInUser.name;
            if (farmerEmailInput) farmerEmailInput.value = loggedInUser.email || "";
            if (farmerPhoneInput) farmerPhoneInput.value = loggedInUser.phone || "";
            if (farmerAddressInput) farmerAddressInput.value = loggedInUser.address || "";
        } else {
            farmerIdInput.value = "101";
            farmerNameInput.value = "anchu";
            if (farmerEmailInput) farmerEmailInput.value = "";
            if (farmerPhoneInput) farmerPhoneInput.value = "";
            if (farmerAddressInput) farmerAddressInput.value = "";
        }
    }
}
