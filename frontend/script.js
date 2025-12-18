const searchBtn = document.getElementById("search-btn");
const searchInput = document.getElementById("search-input");
const resultsDiv = document.getElementById("results");

const queryInfo = document.getElementById("query-info");
const queryTimeSpan = document.getElementById("query-time");
const sortSelect = document.getElementById("sort-select");

let controller;
let allResults = [];
let currentPage = 1;
const resultsPerPage = 10;
const maxPageButtons = 10;

/* =========================
   SEARCH
   ========================= */
searchBtn.addEventListener("click", async () => {
    const query = searchInput.value.trim();
    if (!query) return;

    try {
        const res = await fetch("http://127.0.0.1:8000/search", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ query })
        });

        const data = await res.json();

        // Store & filter results
        allResults = (data.results || []).filter(
            r => r.authors && r.authors.length > 0 && r.publish_time
        );

        // Show query time
        if (data.time_taken !== undefined) {
            queryTimeSpan.textContent = data.time_taken;
            queryInfo.classList.remove("hidden");
        }

        currentPage = 1;
        applySorting(); // sort before rendering

        renderResults();
        renderPagination();

        resultsDiv.scrollIntoView({ behavior: "smooth" });

    } catch (err) {
        console.error("Search failed:", err);
    }
});

/* =========================
   SORTING
   ========================= */
function applySorting() {
    const order = sortSelect.value;

    allResults.sort((a, b) => {
        const dateA = new Date(a.publish_time);
        const dateB = new Date(b.publish_time);
        return order === "latest" ? dateB - dateA : dateA - dateB;
    });
}

sortSelect.addEventListener("change", () => {
    currentPage = 1;
    applySorting();
    renderResults();
    renderPagination();
});

/* =========================
   RENDER RESULTS
   ========================= */
function renderResults() {
    resultsDiv.innerHTML = "";

    const start = (currentPage - 1) * resultsPerPage;
    const end = start + resultsPerPage;
    const pageResults = allResults.slice(start, end);

    pageResults.forEach((r, index) => {
        const authors = r.authors.join(", ");

        const card = document.createElement("div");
        card.className = "result-card";

        const faviconUrl = r.favicon || (r.url
            ? `https://www.google.com/s2/favicons?domain=${new URL(r.url).hostname}`
            : "");

        const faviconImg = faviconUrl
            ? `<img class="favicon" src="${faviconUrl}" alt="favicon" onerror="this.style.display='none'" />`
            : "";

        card.innerHTML = `
            ${faviconImg}
            <div class="result-content">
                <h3>${r.title || "No Title"}</h3>
                <p class="meta">
                    <strong>Authors:</strong> ${authors}<br>
                    <strong>Published:</strong> ${r.publish_time}
                </p>
                <p class="score">
                    <strong>Score:</strong> ${r.score} |
                    <strong>Rank:</strong> ${start + index + 1}
                </p>
                <div class="actions"></div>
            </div>
        `;

        const actionsDiv = card.querySelector(".actions");

        if (r.url) {
            const openWebsiteLink = document.createElement("a");
            openWebsiteLink.href = r.url;
            openWebsiteLink.target = "_blank";
            openWebsiteLink.rel = "noopener noreferrer";
            openWebsiteLink.textContent = "Open Website";
            openWebsiteLink.className = "btn-link";
            actionsDiv.appendChild(openWebsiteLink);
        }

        if (r.path) {
            const openJsonBtn = document.createElement("button");
            openJsonBtn.className = "btn-link";
            openJsonBtn.textContent = "Open JSON";
            openJsonBtn.onclick = () => openJsonFile(encodeURIComponent(r.path));
            actionsDiv.appendChild(openJsonBtn);
        }

        resultsDiv.appendChild(card);
    });

    if (pageResults.length === 0) {
        resultsDiv.innerHTML = `<p>No results found for this page.</p>`;
    }
}

/* =========================
   OPEN JSON FILE
   ========================= */
function openJsonFile(encodedPath) {
    const path = decodeURIComponent(encodedPath);

    fetch(`http://127.0.0.1:8000/json/${path}`)
        .then(res => {
            if (!res.ok) throw new Error("Unable to fetch JSON");
            return res.json();
        })
        .then(json => {
            const win = window.open();
            win.document.write(`
                <html>
                <head>
                    <title>JSON Viewer - ${path}</title>
                    <style>
                        body { font-family: monospace; background:#f4f7f6; padding:20px; }
                        pre { background:white; padding:20px; border-radius:8px; white-space: pre-wrap; }
                    </style>
                </head>
                <body>
                    <h2>JSON File: ${path}</h2>
                    <pre>${JSON.stringify(json, null, 2)}</pre>
                </body>
                </html>
            `);
            win.document.close();
        })
        .catch(() => alert("Unable to load JSON file"));
}

/* =========================
   PAGINATION
   ========================= */
function renderPagination() {
    let pagination = document.getElementById("pagination");

    if (!pagination) {
        pagination = document.createElement("div");
        pagination.id = "pagination";
        resultsDiv.after(pagination);
    }

    pagination.innerHTML = "";
    const totalPages = Math.ceil(allResults.length / resultsPerPage);
    if (!totalPages) return;

    function pageBtn(page) {
        const btn = document.createElement("button");
        btn.textContent = page;
        if (page === currentPage) btn.classList.add("active");
        btn.onclick = () => {
            currentPage = page;
            renderResults();
            renderPagination();
            resultsDiv.scrollIntoView({ behavior: "smooth" });
        };
        return btn;
    }

    if (currentPage > 1) {
        const prev = document.createElement("button");
        prev.textContent = "‹";
        prev.onclick = () => {
            currentPage--;
            renderResults();
            renderPagination();
        };
        pagination.appendChild(prev);
    }

    for (let i = 1; i <= totalPages; i++) {
        pagination.appendChild(pageBtn(i));
    }

    if (currentPage < totalPages) {
        const next = document.createElement("button");
        next.textContent = "›";
        next.onclick = () => {
            currentPage++;
            renderResults();
            renderPagination();
        };
        pagination.appendChild(next);
    }
}

/* =========================
   AUTOCOMPLETE
   ========================= */
searchInput.addEventListener("input", async (e) => {
    const prefix = e.target.value.trim();
    if (prefix.length < 1) {
        clearSuggestions();
        return;
    }

    if (controller) controller.abort();
    controller = new AbortController();

    try {
        const res = await fetch(
            `http://127.0.0.1:8000/autocomplete?q=${encodeURIComponent(prefix)}`,
            { signal: controller.signal }
        );

        const data = await res.json();
        renderSuggestions(data.words);

    } catch (err) {
        if (err.name !== "AbortError") {
            console.error("Autocomplete failed:", err);
        }
    }
});

/* =========================
   AUTOCOMPLETE UI
   ========================= */
function renderSuggestions(words) {
    clearSuggestions();
    if (!words || !words.length) return;

    const box = document.createElement("div");
    box.id = "autocomplete-box";

    words.forEach(word => {
        const item = document.createElement("div");
        item.textContent = word;
       item.onclick = () => {
    const inputValue = searchInput.value;
    const words = inputValue.split(" ");

    // Replace only the last word
    words[words.length - 1] = word;

    searchInput.value = words.join(" ") + " ";
    clearSuggestions();
    searchInput.focus();
};

        box.appendChild(item);
    });

    searchInput.parentNode.appendChild(box);
}

function clearSuggestions() {
    const box = document.getElementById("autocomplete-box");
    if (box) box.remove();
}
