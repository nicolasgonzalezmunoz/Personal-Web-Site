/**
    * Set functions for website theme switching
 */

// Initialize web theme
function calculateSettingAsThemeString({ localStorageTheme, systemSettingLight }) {
    if (localStorageTheme !== null) {
      return localStorageTheme;
    }
  
    if (systemSettingLight.matches) {
      return "light";
    }
  
    return "dark";
};

function updateThemeButton({ buttonEl, isDark }) {
    const newLabel = isDark ? "Change to light theme" : "Change to dark theme";
    buttonEl.setAttribute("aria-label", newLabel);
    const iconEl = buttonEl.firstElementChild;
    iconEl.className = (isDark) ? "fa-solid fa-moon" : "fa-solid fa-sun";
};

function updateFaviconTheme({ isDark }) {
    const favicon = document.getElementById('favicon');
    const favicon16 = document.getElementById('favicon16');
    const favicon32 = document.getElementById('favicon32');
    const faviconApple = document.getElementById('favicon-apple');
    const favicon192 = document.getElementById('favicon192');
    const favicon512 = document.getElementById('favicon512');

    if (isDark){
        favicon.href = "assets/favicon/favicon-dark.ico";
        favicon16.href = "assets/favicon/favicon-16x16-dark.png";
        favicon32.href = "assets/favicon/favicon-32x32-dark.png";
        faviconApple.href = "assets/favicon/apple-touch-icon-dark.png";
        favicon192.href = "assets/favicon/android-chrome-192x192-dark.png";
        favicon512.href = "assets/favicon/android-chrome-512x512-dark.png";
    } else{
        favicon.href = "assets/favicon/favicon-light.ico";
        favicon16.href = "assets/favicon/favicon-16x16-light.png";
        favicon32.href = "assets/favicon/favicon-32x32-light.png";
        faviconApple.href = "assets/favicon/apple-touch-icon-light.png";
        favicon192.href = "assets/favicon/android-chrome-192x192-light.png";
        favicon512.href = "assets/favicon/android-chrome-512x512-light.png";
    }
};

function updateThemeOnHtmlEl({ theme }) {
    document.querySelector("html").setAttribute("data-bs-theme", theme);
};


/**
    * Set functions for web translation
*/
function hideLangElements({lang}){
    const selector = "[lang='" + lang + "']";
    const elements = document.querySelectorAll(selector);
    const nElements = elements.length;
    for (let i = 0; i < nElements; i++){
        elements[i].style.display = 'none';
    }
}

function hideNotLangElements({lang}){
    const selector = "[lang]:not([lang='" + lang + "'])";
    const elements = document.querySelectorAll(selector);
    const nElements = elements.length;
    for (let i = 0; i < nElements; i++){
        elements[i].style.display = 'none';
    }
}

function showLangElements({lang}){
    const selector = "[lang='" + lang + "']";
    const elements = document.querySelectorAll(selector);
    const nElements = elements.length;
    for (let i = 0; i < nElements; i++){
        elements[i].style.display = 'block';
    }
}


function calculateLanguageSettings(){
    langsList = ['en', 'es'];
    // Hide all content in spanish language
    currentLang = document.getElementById('current-lang');
    document.documentElement.setAttribute("lang", 'en');
    currentLang.setAttribute("lang", "en");
    currentLang.innerHTML = "English";
    hideNotLangElements({lang: 'en'});

    // Get Storaged language (if any)
    const selectedLang = localStorage.selectedLang;

    // Check user's preferred languages
    const langs = navigator.languages;

    if (selectedLang !== null){
        setLang = selectedLang;
    } else if (langs !== null){
        const nLangs = langs.length;
        for (let i = 0; i < nLangs; i++){
            let lang = langs[i].slice(0, 2);
            if (langsList.includes(lang)){
                setLang = lang;
                break;
            }
        }
    } else {
        setLang = "en";
    }
    document.documentElement.setAttribute("lang", setLang);
    currentLang.setAttribute("lang", setLang);
    currentLang.innerHTML = 'Español';
                
    hideNotLangElements({lang: setLang});
    showLangElements({lang: setLang});
};


/** 
    *  Set functions for scroll-to-top button
*/
function buttonVisibility ({ scrollButton }) {
    scrollButton.style.visibility = (window.scrollY != 0) ? "visible" : "hidden";
};


window.addEventListener('DOMContentLoaded', (event) => {

    //------------------Handdle website theme---------------
    const themeButton = document.getElementById("switch-theme-button");
    const localStorageTheme = localStorage.getItem("theme");
    const systemSettingLight = window.matchMedia("(prefers-color-scheme: light)");

    let currentThemeSetting = calculateSettingAsThemeString({ localStorageTheme, systemSettingLight });

    updateThemeButton({ buttonEl: themeButton, isDark: currentThemeSetting === "dark" });
    updateFaviconTheme({ isDark: currentThemeSetting === "dark" });
    updateThemeOnHtmlEl({ theme: currentThemeSetting });


    themeButton.addEventListener("click", (event) => {
        const newTheme = (currentThemeSetting === "dark") ? "light" : "dark";
    
        localStorage.setItem("theme", newTheme);
        updateThemeButton({ buttonEl: themeButton, isDark: (newTheme === "dark") });
        updateFaviconTheme({ isDark: newTheme === "dark" });
        updateThemeOnHtmlEl({ theme: newTheme });
    
        currentThemeSetting = newTheme;
    });

    //-------------------Handle webiste language------------
    const langButtonEn = document.getElementById('lang-en');
    const langButtonEs = document.getElementById('lang-es');
    const currentLangEl = document.getElementById('current-lang');

    calculateLanguageSettings();


    langButtonEn.addEventListener("click", (event) => {
        const currentLang = currentLangEl.lang;
        if (currentLang !== 'en'){
            document.documentElement.setAttribute("lang", 'en');
            currentLangEl.setAttribute("lang", 'en');
            currentLangEl.innerHTML = 'English';
            hideLangElements({lang: currentLang});
            showLangElements({lang: "en"});
            // Write the selected language on local storage
            localStorage && (localStorage.selectedLang = "en");
        }
    });


    langButtonEs.addEventListener("click", (event) => {
        const currentLang = currentLangEl.lang;
        if (currentLang !== 'es'){
            document.documentElement.setAttribute("lang", 'es');
            currentLangEl.setAttribute("lang", 'es');
            currentLangEl.innerHTML = 'Español';
            hideLangElements({lang: currentLang});
            showLangElements({lang: "es"});
            // Write the selected language on local storage
            localStorage && (localStorage.selectedLang = "es");
        }
    });


    // Handle scroll-to-top button
    //**
    const scrollButton = document.getElementById("scroll-to-top");
    document.addEventListener("scroll", (event) => {
        buttonVisibility({scrollButton: scrollButton});
    });

    scrollButton.addEventListener("click", () => {
        window.scrollTo({
            top: 0,
            behavior: "smooth"
        });
    });
    
});