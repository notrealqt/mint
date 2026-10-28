// Doorway rice — let Firefox load chrome/userChrome.css + userContent.css
user_pref("toolkit.legacyUserProfileCustomizations.stylesheets", true);
// follow the dark system theme for sites and built-in pages
user_pref("layout.css.prefers-color-scheme.content-override", 0);

// tabs sit in the title bar (no separate title bar) — one header with the panel (README #9)
user_pref("browser.tabs.inTitlebar", 1);
