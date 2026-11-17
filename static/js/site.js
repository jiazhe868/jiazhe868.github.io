/* Small progressive enhancements. The site works without JavaScript. */
(function () {
  "use strict";

  var root = document.documentElement;
  root.classList.add("js");

  /* ---- theme toggle (the initial theme is set inline in <head>) ---- */
  var toggle = document.querySelector(".theme-toggle");
  if (toggle) {
    toggle.addEventListener("click", function () {
      var dark = root.getAttribute("data-theme") === "dark" ||
        (!root.getAttribute("data-theme") && window.matchMedia("(prefers-color-scheme: dark)").matches);
      var next = dark ? "light" : "dark";
      root.setAttribute("data-theme", next);
      try { localStorage.setItem("theme", next); } catch (e) { /* storage unavailable */ }
    });
  }

  /* ---- header border once the page scrolls ---- */
  var header = document.querySelector(".site-header");
  if (header) {
    var onScroll = function () { header.classList.toggle("is-scrolled", window.scrollY > 8); };
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
  }

  /* ---- mobile menu ---- */
  var menuBtn = document.querySelector(".menu-toggle");
  var nav = document.querySelector(".nav");
  if (menuBtn && nav) {
    menuBtn.addEventListener("click", function () {
      var open = nav.classList.toggle("is-open");
      menuBtn.setAttribute("aria-expanded", open ? "true" : "false");
    });
    nav.addEventListener("click", function (e) {
      if (e.target.tagName === "A") { nav.classList.remove("is-open"); menuBtn.setAttribute("aria-expanded", "false"); }
    });
  }

  /* ---- lightbox for figures ---- */
  var box = document.querySelector(".lightbox");
  if (box && typeof box.showModal === "function") {
    var boxImg = box.querySelector("img");
    var boxCap = box.querySelector("p");
    document.addEventListener("click", function (e) {
      var link = e.target.closest("a.zoom");
      if (!link) return;
      e.preventDefault();
      var img = link.querySelector("img");
      boxImg.src = link.getAttribute("href");
      boxImg.alt = img ? img.alt : "";
      boxCap.textContent = link.getAttribute("data-caption") || "";
      boxCap.hidden = !boxCap.textContent;
      box.showModal();
    });
    box.addEventListener("click", function (e) {
      if (e.target === box || e.target.closest(".close") || e.target === boxImg) box.close();
    });
    box.addEventListener("close", function () { boxImg.removeAttribute("src"); });
  }

  /* ---- table of contents: highlight the section in view ---- */
  var tocLinks = document.querySelectorAll(".toc a");
  if (tocLinks.length && "IntersectionObserver" in window) {
    var byId = {};
    tocLinks.forEach(function (a) { byId[decodeURIComponent(a.hash.slice(1))] = a; });
    var headings = Object.keys(byId).map(function (id) { return document.getElementById(id); }).filter(Boolean);
    var current = null;
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) {
          if (current) current.classList.remove("is-active");
          current = byId[en.target.id];
          if (current) current.classList.add("is-active");
        }
      });
    }, { rootMargin: "-20% 0px -70% 0px" });
    headings.forEach(function (h) { io.observe(h); });
  }

  /* ---- earthquake gallery filters ---- */
  var filterBar = document.querySelector(".filters");
  if (filterBar) {
    var items = document.querySelectorAll("[data-themes]");
    filterBar.addEventListener("click", function (e) {
      var btn = e.target.closest("button");
      if (!btn) return;
      var key = btn.getAttribute("data-filter");
      filterBar.querySelectorAll("button").forEach(function (b) {
        b.setAttribute("aria-pressed", b === btn ? "true" : "false");
      });
      items.forEach(function (el) {
        var themes = el.getAttribute("data-themes").split(" ");
        el.hidden = !(key === "all" || themes.indexOf(key) !== -1);
      });
      document.querySelectorAll("[data-group]").forEach(function (g) {
        g.hidden = !g.querySelector("[data-themes]:not([hidden])");
      });
    });
  }

  /* ---- publication search ---- */
  var search = document.querySelector(".pub-search");
  if (search) {
    var pubs = document.querySelectorAll(".pub");
    var count = document.querySelector(".pub-count");
    search.addEventListener("input", function () {
      var q = search.value.trim().toLowerCase();
      var shown = 0;
      pubs.forEach(function (p) {
        var hit = !q || p.textContent.toLowerCase().indexOf(q) !== -1;
        p.hidden = !hit;
        if (hit) shown += 1;
      });
      document.querySelectorAll(".pub-year").forEach(function (y) {
        y.hidden = !y.querySelector(".pub:not([hidden])");
      });
      if (count) count.textContent = shown + (shown === 1 ? " paper" : " papers");
    });
  }
})();
