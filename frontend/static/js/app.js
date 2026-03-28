const translations = {
    en: {
        dashboard: "Dashboard",
        evaluations: "Evaluations",
        submissions: "Submissions",
        settings: "Settings",
        logout: "Logout",
        score: "Score",
        hi: "Welcome",
        dark_mode: "Dark Mode",
        login_title: "Login",
        username: "Username",
        password: "Password",
        submit_evidence: "Submit Evidence",
        pending_subs: "Pending Submissions",
        create_member: "Create Member",
        member_evals: "Member Evaluations",
        meetings: "Meetings",
        events: "Events",
        tasks: "Tasks"
    },
    ar: {
        dashboard: "لوحة التحكم",
        evaluations: "التقييمات",
        submissions: "التكليفات",
        settings: "الإعدادات",
        logout: "تسجيل الخروج",
        score: "الدرجة",
        hi: "أهلاً بك",
        dark_mode: "الوضع الليلي",
        login_title: "تسجيل الدخول",
        username: "اسم المستخدم",
        password: "كلمة المرور",
        submit_evidence: "تقديم التكليف",
        pending_subs: "تكليفات قيد المراجعة",
        create_member: "إنشاء عضو جديد",
        member_evals: "تقييم الأعضاء",
        meetings: "الاجتماعات",
        events: "الفعاليات",
        tasks: "المهام"
    }
};

function initLanguage() {
    const savedLang = localStorage.getItem('lang') || 'ar';
    setLanguage(savedLang);
}

function setLanguage(lang) {
    document.documentElement.lang = lang;
    document.documentElement.setAttribute('dir', lang === 'ar' ? 'rtl' : 'ltr');
    localStorage.setItem('lang', lang);
    
    // Update all elements with data-i18n
    document.querySelectorAll('[data-i18n]').forEach(el => {
        const key = el.getAttribute('data-i18n');
        el.textContent = translations[lang][key] || key;
    });
}

function initTheme() {
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
}

function toggleTheme() {
    const currentTheme = document.documentElement.getAttribute('data-theme');
    const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
}

document.addEventListener('DOMContentLoaded', () => {
    initLanguage();
    initTheme();
    
    const themeBtn = document.getElementById('theme-toggle');
    if (themeBtn) themeBtn.addEventListener('click', toggleTheme);
    
    const langBtn = document.getElementById('lang-toggle');
    if (langBtn) langBtn.addEventListener('click', () => {
        const currentLang = document.documentElement.lang;
        setLanguage(currentLang === 'ar' ? 'en' : 'ar');
    });
});
