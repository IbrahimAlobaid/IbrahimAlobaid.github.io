(() => {
  const nav = document.getElementById("nav");
  const menuBtn = document.getElementById("menu-btn");
  const links = [...document.querySelectorAll(".nav__links a")];

  /* Old links used ?lang=ar — Arabic now lives at /ar/ */
  if (new URLSearchParams(location.search).get("lang") === "ar" && !location.pathname.startsWith("/ar")) {
    location.replace("/ar/" + location.hash);
    return;
  }

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
