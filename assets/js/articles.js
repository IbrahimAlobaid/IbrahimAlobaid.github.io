(() => {
  const prose = document.querySelector(".prose");

  /* ---------------- Reading progress ---------------- */
  const bar = document.querySelector(".read-progress span");
  if (bar && prose) {
    let ticking = false;
    const update = () => {
      const r = prose.getBoundingClientRect();
      const total = r.height - window.innerHeight * 0.6;
      const done = Math.min(1, Math.max(0, -r.top / Math.max(total, 1)));
      bar.style.transform = `scaleX(${done})`;
      ticking = false;
    };
    window.addEventListener("scroll", () => { if (!ticking) { ticking = true; requestAnimationFrame(update); } }, { passive: true });
    update();
  }

  /* ---------------- Copy buttons on code blocks ---------------- */
  if (prose && navigator.clipboard) {
    const label = prose.dataset.copy || "Copy";
    const done = prose.dataset.copied || "Copied";
    prose.querySelectorAll("pre.code").forEach((pre) => {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "code-copy";
      btn.textContent = label;
      btn.addEventListener("click", async () => {
        try {
          await navigator.clipboard.writeText(pre.querySelector("code").innerText);
          btn.textContent = done;
          btn.classList.add("is-done");
          setTimeout(() => { btn.textContent = label; btn.classList.remove("is-done"); }, 1800);
        } catch { /* clipboard blocked — leave the code selectable */ }
      });
      pre.appendChild(btn);
    });
  }

  /* ---------------- TOC: active section + collapse on small screens ---------------- */
  const toc = document.querySelector(".toc");
  if (toc) {
    const box = toc.querySelector("details");
    if (box && window.matchMedia("(max-width: 1180px)").matches) box.open = false;
    const links = [...toc.querySelectorAll("a")];
    const targets = links.map((a) => document.getElementById(decodeURIComponent(a.hash.slice(1)))).filter(Boolean);
    if ("IntersectionObserver" in window && targets.length) {
      const spy = new IntersectionObserver(
        (entries) => {
          entries.forEach((e) => {
            if (!e.isIntersecting) return;
            links.forEach((a) => a.classList.toggle("is-active", decodeURIComponent(a.hash.slice(1)) === e.target.id));
          });
        },
        { rootMargin: "-20% 0px -70% 0px" }
      );
      targets.forEach((t) => spy.observe(t));
    }
    links.forEach((a) => a.addEventListener("click", () => {
      if (box && window.matchMedia("(max-width: 1180px)").matches) box.open = false;
    }));
  }
})();
