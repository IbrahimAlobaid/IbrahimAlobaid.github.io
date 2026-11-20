(() => {
  const root = document.documentElement;
  const nav = document.getElementById("nav");
  const menuBtn = document.getElementById("menu-btn");
  const langBtn = document.getElementById("lang-toggle");
  const links = [...document.querySelectorAll(".nav__links a")];

  /* ---------------- Language ---------------- */
  const AR = window.I18N_AR || {};
  const textNodes = [...document.querySelectorAll("[data-i18n]")];
  const altNodes = [...document.querySelectorAll("[data-i18n-alt]")];
  // Snapshot the English markup so switching back is lossless.
  const EN = {};
  textNodes.forEach((el) => (EN[el.dataset.i18n] = el.innerHTML));
  altNodes.forEach((el) => (EN["alt:" + el.dataset.i18nAlt] = el.alt));
  const titles = {
    en: document.title,
    ar: "إبراهيم العبيد — مهندس ذكاء اصطناعي رئيسي وباني مجتمعات",
  };

  const store = {
    get() { try { return localStorage.getItem("lang"); } catch { return null; } },
    set(v) { try { localStorage.setItem("lang", v); } catch { /* storage unavailable */ } },
  };

  function setLang(lang) {
    const ar = lang === "ar";
    root.lang = ar ? "ar" : "en";
    root.dir = ar ? "rtl" : "ltr";
    textNodes.forEach((el) => {
      const key = el.dataset.i18n;
      const value = ar ? AR[key] : EN[key];
      if (value != null) el.innerHTML = value;
    });
    altNodes.forEach((el) => {
      const key = el.dataset.i18nAlt;
      const value = ar ? AR[key] : EN["alt:" + key];
      if (value != null) el.alt = value;
    });
    document.title = titles[ar ? "ar" : "en"];
    langBtn.innerHTML = ar ? '<span lang="en">EN</span>' : '<span lang="ar">ع</span>';
    langBtn.setAttribute("aria-label", ar ? "Switch to English" : "التبديل إلى العربية");
    store.set(root.lang);
  }

  langBtn.addEventListener("click", () => setLang(root.lang === "ar" ? "en" : "ar"));
  const params = new URLSearchParams(location.search);
  const initial = params.get("lang") || store.get();
  if (initial === "ar") setLang("ar");

  /* ---------------- Mobile menu ---------------- */
  function closeMenu() {
    document.body.classList.remove("menu-open");
    menuBtn.setAttribute("aria-expanded", "false");
  }
  menuBtn.addEventListener("click", () => {
    const open = document.body.classList.toggle("menu-open");
    menuBtn.setAttribute("aria-expanded", String(open));
  });
  links.forEach((a) => a.addEventListener("click", closeMenu));
  document.addEventListener("keydown", (e) => e.key === "Escape" && closeMenu());

  /* ---------------- Nav state ---------------- */
  const onScroll = () => nav.classList.toggle("is-scrolled", window.scrollY > 24);
  onScroll();
  window.addEventListener("scroll", onScroll, { passive: true });

  // Spy on every top-level section so sections without a nav link
  // (hero, credentials) clear the highlight instead of leaving a stale one.
  const sections = [...document.querySelectorAll("main > section[id]")];

  if ("IntersectionObserver" in window) {
    const spy = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (!entry.isIntersecting) return;
          links.forEach((a) =>
            a.classList.toggle("is-active", a.getAttribute("href") === "#" + entry.target.id)
          );
        });
      },
      { rootMargin: "-45% 0px -50% 0px" }
    );
    sections.forEach((s) => spy.observe(s));

    /* ---------------- Reveal on scroll ---------------- */
    const reveal = new IntersectionObserver(
      (entries, obs) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            entry.target.classList.add("is-in");
            obs.unobserve(entry.target);
          }
        });
      },
      { rootMargin: "0px 0px -8% 0px", threshold: 0.08 }
    );
    document.querySelectorAll(".reveal").forEach((el) => reveal.observe(el));
  } else {
    document.querySelectorAll(".reveal").forEach((el) => el.classList.add("is-in"));
  }

  /* ---------------- Footer year ---------------- */
  const year = document.getElementById("year");
  if (year) year.textContent = new Date().getFullYear();
})();
