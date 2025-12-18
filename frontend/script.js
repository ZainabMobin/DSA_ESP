// const searchBtn = document.getElementById("search-btn");
// const searchInput = document.getElementById("search-input");
// const resultsDiv = document.getElementById("results");

// searchBtn.addEventListener("click", async () => {
//     const query = searchInput.value.trim();
//     if (!query) return;

//     try {
//         const res = await fetch("http://127.0.0.1:8000/search-query", {
//             method: "POST",
//             headers: {
//                 "Content-Type": "application/json"
//             },
//             body: JSON.stringify({ query })
//         });

//         const data = await res.json();

//         // Simple render
//         resultsDiv.innerHTML = "";
//         data.results.forEach(r => {
//             const p = document.createElement("p");

//             // Combine title and authors
//             const authors = r.authors && r.authors.length > 0 ? r.authors.join(", ") : "Unknown authors";
//             p.textContent = `${r.title} — Authors: ${authors}`;

//             resultsDiv.appendChild(p);
//         });


//     } catch (err) {
//         console.error("Search failed:", err);
//     }
// });

const searchBtn = document.getElementById("search-btn");
const searchInput = document.getElementById("search-input");
const resultsDiv = document.getElementById("results");

let controller; // abort previous autocomplete calls

/* =========================
   SEARCH BUTTON (EXISTING)
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
        resultsDiv.innerHTML = "";

        data.results.forEach(r => {
            const authors = r.authors?.length ? r.authors.join(", ") : "Unknown authors";
            const div = document.createElement("div");
            div.classList.add("result-item"); // optional: for styling

            div.innerHTML = `
                <strong>Title:</strong> ${r.title || "N/A"} <br>
                <strong>Authors:</strong> ${authors} <br>
                <strong>Score:</strong> ${r.score} <br>
                <strong>DocID:</strong> ${r.docID} <br>
                <strong>Path:</strong> ${r.path || "N/A"} <br>
                <strong>Publish Date:</strong> ${r.publish_time || "N/A"} <br>
                <strong>URL:</strong> ${r.url ? `<a href="${r.url}" target="_blank">${r.url}</a>` : "N/A"}
            `;

            resultsDiv.appendChild(div);
            resultsDiv.appendChild(document.createElement("hr")); // separator
        });
        // const data = await res.json();

        // resultsDiv.innerHTML = "";
        // data.results.forEach(r => {
        //     const p = document.createElement("p");
        //     const authors = r.authors?.length ? r.authors.join(", ") : "Unknown authors";
        //     p.textContent = `${r.title} — Authors: ${authors}`;
        //     resultsDiv.appendChild(p);
        // });

    } catch (err) {
        console.error("Search failed:", err);
    }
});


/* =========================
   AUTOCOMPLETE TRIGGER
   ========================= */
searchInput.addEventListener("input", async (e) => {
    const prefix = e.target.value.trim();
    if (prefix.length < 1) {
        clearSuggestions();
        return;
    }

    // cancel previous request
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
    if (!words || words.length === 0) return;

    const box = document.createElement("div");
    box.id = "autocomplete-box";
    box.style.border = "1px solid #ccc";
    box.style.background = "#fff";

    words.forEach(word => {
        const item = document.createElement("div");
        item.textContent = word;
        item.style.padding = "6px";
        item.style.cursor = "pointer";

        item.onclick = () => {
            searchInput.value = word;
            clearSuggestions();
        };

        box.appendChild(item);
    });

    searchInput.parentNode.appendChild(box);
}

function clearSuggestions() {
    const box = document.getElementById("autocomplete-box");
    if (box) box.remove();
}
