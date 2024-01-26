
/** Calculate the current theme setting or fallback to dark mode.*/
function calculateSettingAsThemeString({ localStorageTheme, systemSettingLight }) {
    if (localStorageTheme !== null) {
      return localStorageTheme;
    }
  
    if (systemSettingLight.matches) {
      return "light";
    }
  
    return "dark";
}

/** Update switch theme button's icon and aria label */
function updateButton({ buttonEl, isDark }) {
    const newLabel = isDark ? "Change to light theme" : "Change to dark theme";
    // use an aria-label if you are omitting text on the button
    // and using a sun/moon icon, for example
    buttonEl.setAttribute("aria-label", newLabel);
    const iconEl = buttonEl.firstElementChild;
    iconEl.className = (isDark) ? "fa-solid fa-moon" : "fa-solid fa-sun";
}

/** Update theme settings on the html tag */
function updateThemeOnHtmlEl({ theme }) {
    document.querySelector("html").setAttribute("data-bs-theme", theme);
}

/**
* On page load:
*/

window.addEventListener('DOMContentLoaded', (event) => {
  
    /**
    * 1. Grab what we need from the DOM and system settings on page load
    */
    //const button = document.querySelector("[data-theme-toggle]");
    const button = document.getElementById("switch-theme-button");
    const localStorageTheme = localStorage.getItem("theme");
    const systemSettingLight = window.matchMedia("(prefers-color-scheme: light)");
    
    /**
    * 2. Work out the current site settings
    */
    let currentThemeSetting = calculateSettingAsThemeString({ localStorageTheme, systemSettingLight });
    
    /**
    * 3. Update the theme setting and button text accoridng to current settings
    */
    updateButton({ buttonEl: button, isDark: currentThemeSetting === "dark" });
    updateThemeOnHtmlEl({ theme: currentThemeSetting });
    
    /**
    * 4. Add an event listener to toggle the theme
    */

    button.addEventListener("click", (event) => {
        const newTheme = (currentThemeSetting === "dark") ? "light" : "dark";
    
        localStorage.setItem("theme", newTheme);
        updateButton({ buttonEl: button, isDark: (newTheme === "dark") });
        updateThemeOnHtmlEl({ theme: newTheme });
    
        currentThemeSetting = newTheme;
    });
});