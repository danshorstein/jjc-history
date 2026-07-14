// Router + boot.
import {
  viewHome, viewTimeMachine, viewPeople, viewStories, viewThenNow,
  viewMysteries, viewSearch, surpriseMe,
} from "./views.js";
import { closeModal } from "./ui.js";

const main = document.querySelector("main");

const routes = [
  [/^#?\/?$/, () => viewHome(main)],
  [/^#\/time-machine(?:\/(\d+))?$/, m => viewTimeMachine(main, m[1])],
  [/^#\/people(?:\/(.+))?$/, m => viewPeople(main, m[1] ? decodeURIComponent(m[1]) : null)],
  [/^#\/stories$/, () => viewStories(main)],
  [/^#\/story\/(.+)$/, m => viewStories(main, m[1])],
  [/^#\/then-now$/, () => viewThenNow(main)],
  [/^#\/mysteries$/, () => viewMysteries(main)],
  [/^#\/search(?:\/(.+))?$/, m => viewSearch(main, m[1] ? decodeURIComponent(m[1]) : null)],
];

const NAV_KEY = {
  "": "home", "time-machine": "time-machine", people: "people",
  stories: "stories", story: "stories", "then-now": "then-now",
  mysteries: "mysteries", search: "search",
};

async function route() {
  const hash = location.hash || "#/";
  closeModal();
  main.innerHTML = "";
  const seg = (hash.split("/")[1] || "").split("/")[0];
  const key = NAV_KEY[seg] ?? "home";
  document.querySelectorAll(".nav a").forEach(a => {
    a.classList.toggle("active", a.dataset.nav === key);
  });
  for (const [rx, fn] of routes) {
    const m = hash.match(rx);
    if (m) {
      try {
        await fn(m);
      } catch (err) {
        main.innerHTML = "";
        const p = document.createElement("p");
        p.className = "empty";
        p.textContent = `Something went wrong loading this view: ${err.message}. ` +
          "If you opened index.html directly, run a local server from the project root instead " +
          "(python3 -m http.server) so the data files can load.";
        main.append(p);
        console.error(err);
      }
      window.scrollTo(0, 0);
      return;
    }
  }
  location.hash = "#/";
}

window.addEventListener("hashchange", route);
route();

document.getElementById("surprise-btn").addEventListener("click", surpriseMe);

// theme toggle: light <-> dark, persisted
const themeBtn = document.getElementById("theme-btn");
const savedTheme = localStorage.getItem("ldvd-theme");
if (savedTheme) document.documentElement.dataset.theme = savedTheme;
themeBtn.addEventListener("click", () => {
  const cur = document.documentElement.dataset.theme ||
    (matchMedia("(prefers-color-scheme: dark)").matches ? "dark" : "light");
  const next = cur === "dark" ? "light" : "dark";
  document.documentElement.dataset.theme = next;
  localStorage.setItem("ldvd-theme", next);
});
