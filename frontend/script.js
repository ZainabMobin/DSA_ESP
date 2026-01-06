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

        if (r.docID !== undefined) {
            const openJsonBtn = document.createElement("button");
            openJsonBtn.className = "btn-link";
            openJsonBtn.textContent = "Open JSON";
            openJsonBtn.onclick = () => openJsonFile(r.docID, r.title);
            actionsDiv.appendChild(openJsonBtn);
        }

        resultsDiv.appendChild(card);
    });

    if (pageResults.length === 0) {
        resultsDiv.innerHTML = `<p>No results found for this page.</p>`;
    }
}

function escapeHtml(str) {
    if (!str) return "";
    return String(str)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}

function renderDocument(json) {
    const meta = json.metadata || {};
    let html = `<div class="document-renderer">`;

    // Paper ID
    html += `<div class="section paper-id">
        <p><strong>Paper ID:</strong> ${escapeHtml(json.paper_id || "Paper ID not available")}</p>
    </div>`;

    // Title
    html += `<div class="section">
        <h2>Title</h2>
        <p class="document-title">${escapeHtml(meta.title || "Title not available")}</p>
    </div>`;

    // Authors
    html += `<div class="section">
        <h2>Authors</h2>`;
    const authors = meta.authors || json.authors;
    if (authors && authors.length > 0) {
        html += `<ul>`;
        authors.forEach(a => {
            html += `<li>${escapeHtml(
                `${a.first || ""} ${a.middle?.join(" ") || ""} ${a.last || ""}`
            )} - ${escapeHtml(a.affiliation?.institution || "[institution not available]")} (${escapeHtml(a.email || "[email not available]")})</li>`;
        });
        html += `</ul>`;
    } else {
        html += `<p>Authors not available</p>`;
    }
    html += `</div>`;

    // Abstract
    const abstract = meta.abstract || json.abstract;
    html += `<div class="section">
        <h2>Abstract</h2>`;
    if (abstract && abstract.length > 0) {
        abstract.forEach(p => {
            html += `<p>${escapeHtml(p.text)}</p>`;
        });
    } else {
        html += `<p>Abstract not available</p>`;
    }
    html += `</div>`;

    // Body Text
    const bodyText = meta.body_text || json.body_text;
    html += `<div class="section">
        <h2>Body Text</h2>`;
    if (bodyText && bodyText.length > 0) {
        bodyText.forEach(p => {
            html += `<div class="paragraph"><h3>${escapeHtml(p.section || "Section")}</h3><p>${escapeHtml(p.text)}</p></div>`;
        });
    } else {
        html += `<p>Body Text not available</p>`;
    }
    html += `</div>`;

    // Bibliography
    const bibEntries = meta.bib_entries || json.bib_entries;
    html += `<div class="section">
        <h2>Bibliography</h2>`;
    if (bibEntries && Object.keys(bibEntries).length > 0) {
        html += `<ul>`;
        Object.entries(bibEntries).forEach(([id, entry]) => {
            html += `<li><strong>${escapeHtml(id)}</strong>: ${escapeHtml(entry.title || "[title not available]")} (${entry.year || "[year not available]"})</li>`;
        });
        html += `</ul>`;
    } else {
        html += `<p>Bib Entries not available</p>`;
    }
    html += `</div>`;

    // Reference Entries
    const refEntries = meta.ref_entries || json.ref_entries;
    html += `<div class="section">
        <h2>Figures & Tables</h2>`;
    if (refEntries && Object.keys(refEntries).length > 0) {
        html += `<ul>`;
        Object.entries(refEntries).forEach(([id, entry]) => {
            html += `<li><strong>${escapeHtml(id)}</strong> (${escapeHtml(entry.type)}): ${escapeHtml(entry.text || "[caption not available]")}</li>`;
        });
        html += `</ul>`;
    } else {
        html += `<p>Reference Entries not available</p>`;
    }
    html += `</div>`;

    // Back Matter
    const backMatter = meta.back_matter || json.back_matter;
    html += `<div class="section">
        <h2>Back Matter</h2>`;
    if (backMatter && backMatter.length > 0) {
        backMatter.forEach(p => {
            html += `<div class="paragraph"><h3>${escapeHtml(p.section || "Section")}</h3><p>${escapeHtml(p.text)}</p></div>`;
        });
    } else {
        html += `<p>Back Matter not available</p>`;
    }
    html += `</div>`;

    html += `</div>`;
    return html;
}

/* =========================
   OPEN JSON FILE
============================= */
function openJsonFile(docID, title) {
    console.log("🟡 openJsonFile() called, docID:", docID);

    fetch(`http://127.0.0.1:8000/json/${docID}`)
        .then(res => {
            console.log("🟢 Response received:", res.status, res.statusText);
            if (!res.ok) throw new Error("Unable to fetch JSON");
            return res.json();
        })
        .then(json => {
            console.log("🟢 JSON parsed successfully");
            
            const win = window.open("", "_blank");
            console.log("win is", win);
            win.document.open();
            win.document.write(`
                <html>
                <head>
                    <title>${title}</title>
                    <link rel="stylesheet" href="/static/styles.css" />
                </head>
                <body>
                    ${renderDocument(json)}
                </body>
                </html>
            `);
            win.document.close();
        })
        .catch(() => {
            console.log("Unable to fetch json parse");
            alert("Unable to load JSON file") 
        });
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


// add file option

const openBtn = document.getElementById("openUploadModal");
const modal = document.getElementById("uploadModal");
const closeBtn = document.getElementById("closeUploadModal");

openBtn.onclick = () => {
  modal.style.display = "block";
};

closeBtn.onclick = () => {
  modal.style.display = "none";
};

window.onclick = (event) => {
  if (event.target === modal) {
    modal.style.display = "none";
  }
};

