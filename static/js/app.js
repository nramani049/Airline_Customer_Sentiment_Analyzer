/**
 * app.js - Airline Customer Sentiment Analyzer Frontend Logic
 * Vanilla JavaScript managing themes, asynchronous API calls, Chart.js instances, and DOM updates.
 */

// Global state
let currentTheme = localStorage.getItem("sma_theme") || "light";
let currentFreq = "monthly"; // "monthly" or "daily"
let allAvailableAirlines = [];
let allReviewsCache = [];

// Chart.js instances
let chartDistInstance = null;
let chartAirlineInstance = null;
let chartTrendInstance = null;

// Debounce timer for smooth filter updates
let filterDebounceTimer = null;

// =========================================================
// 1. THEME SWITCHER (ANIMATED SUN/MOON TOGGLE)
// =========================================================
function initTheme() {
    document.documentElement.setAttribute("data-theme", currentTheme);

    const toggleBtn = document.getElementById("themeToggleBtn");
    if (toggleBtn) {
        toggleBtn.addEventListener("click", () => {
            currentTheme = currentTheme === "light" ? "dark" : "light";
            document.documentElement.setAttribute("data-theme", currentTheme);
            localStorage.setItem("sma_theme", currentTheme);
            updateAllChartThemes();
        });
    }
}

function getThemeColors() {
    const isDark = currentTheme === "dark";
    return {
        text: isDark ? "#F4F5FA" : "#172033",
        secondaryText: isDark ? "#B7BDCB" : "#5F6B7A",
        mutedText: isDark ? "#929AAC" : "#778196",
        border: isDark ? "#2B3040" : "#E3E7EF",
        cardBg: isDark ? "#191D28" : "#FFFFFF",
        accent: isDark ? "#9270FF" : "#6D3DF5",
        positive: isDark ? "#35C98A" : "#159A63",
        negative: isDark ? "#FF6666" : "#DC4545",
        neutral: isDark ? "#A0A7B5" : "#778196",
        gridLine: isDark ? "#2B3040" : "#E3E7EF",
    };
}

// =========================================================
// 2. DATA FETCHING & FILTER DISPATCHER
// =========================================================
function buildFilterQueryParams() {
    const params = new URLSearchParams();

    // Selected airlines
    const airlineCheckboxes = document.querySelectorAll(".airline-checkbox:checked");
    const selectedAirlines = Array.from(airlineCheckboxes).map(cb => cb.value);
    if (selectedAirlines.length > 0 && selectedAirlines.length < allAvailableAirlines.length) {
        params.set("airlines", selectedAirlines.join(","));
    }

    // Selected sentiments
    const sentimentCheckboxes = document.querySelectorAll(".sentiment-checkbox:checked");
    const selectedSentiments = Array.from(sentimentCheckboxes).map(cb => cb.value);
    if (selectedSentiments.length > 0 && selectedSentiments.length < 3) {
        params.set("sentiments", selectedSentiments.join(","));
    }

    // Dates
    const startVal = document.getElementById("startDateInput")?.value;
    const endVal = document.getElementById("endDateInput")?.value;
    if (startVal) params.set("start_date", startVal);
    if (endVal) params.set("end_date", endVal);

    params.set("freq", currentFreq);
    return params.toString();
}

async function fetchDashboardData(isInitial = false) {
    try {
        const query = buildFilterQueryParams();
        const url = `/api/dashboard?${query}`;

        const res = await fetch(url);
        if (!res.ok) throw new Error(`HTTP Error ${res.status}`);
        const data = await res.json();

        if (data.status === "success") {
            renderDashboard(data, isInitial);
        } else {
            console.error("Dashboard error:", data.message);
        }
    } catch (err) {
        console.error("Failed to fetch dashboard data:", err);
    }
}

function debouncedFilterUpdate() {
    clearTimeout(filterDebounceTimer);
    filterDebounceTimer = setTimeout(() => {
        fetchDashboardData();
    }, 180);
}

// =========================================================
// 3. RENDER DASHBOARD (KPIS, CHARTS, TABLE)
// =========================================================
function renderDashboard(data, isInitial) {
    // 1. Meta & Source Badge
    const sourceText = document.getElementById("sourceNameText");
    if (sourceText) sourceText.textContent = data.meta.source_name;

    // 2. Initial Setup: Populate Airlines & Date inputs if empty
    if (isInitial || allAvailableAirlines.length === 0) {
        allAvailableAirlines = data.filters.available_airlines || [];
        populateAirlineFilter(allAvailableAirlines, data.filters.selected_airlines);
        populateManualAirlineSelect(allAvailableAirlines);

        const startInput = document.getElementById("startDateInput");
        const endInput = document.getElementById("endDateInput");
        if (startInput && !startInput.value) {
            startInput.value = data.filters.min_date;
            startInput.min = data.filters.min_date;
            startInput.max = data.filters.max_date;
        }
        if (endInput && !endInput.value) {
            endInput.value = data.filters.max_date;
            endInput.min = data.filters.min_date;
            endInput.max = data.filters.max_date;
        }
    }

    // 3. KPIs
    const k = data.kpis;
    document.getElementById("kpiTotal").textContent = k.total;
    document.getElementById("kpiTotalBadge").textContent = `${data.meta.filtered_records} of ${data.meta.total_records}`;

    document.getElementById("kpiPositive").textContent = k.positive;
    document.getElementById("kpiPositivePercent").textContent = `${k.pos_percent}%`;

    document.getElementById("kpiNegative").textContent = k.negative;
    document.getElementById("kpiNegativePercent").textContent = `${k.neg_percent}%`;

    document.getElementById("kpiNeutral").textContent = k.neutral;
    document.getElementById("kpiNeutralPercent").textContent = `${k.neu_percent}%`;

    // 4. Render Charts
    renderDistributionChart(data.charts.distribution);
    renderAirlineComparisonChart(data.charts.airline_comparison);
    renderDateTrendChart(data.charts.date_trend);

    // 5. Render Reviews Table
    allReviewsCache = data.reviews || [];
    renderReviewsTable(allReviewsCache);

    // 6. Update Export URLs to match active filters
    const query = buildFilterQueryParams();
    document.getElementById("btnExportCSV").href = `/api/export/csv?${query}`;
    document.getElementById("btnExportPDF").href = `/api/export/pdf?${query}`;
}

// Populate airline checkboxes in sidebar
function populateAirlineFilter(allAirlines, selectedAirlines) {
    const container = document.getElementById("airlineCheckboxList");
    if (!container) return;
    container.innerHTML = "";

    allAirlines.forEach(airline => {
        const isChecked = selectedAirlines.includes(airline);
        const label = document.createElement("label");
        label.className = "checkbox-item";
        label.innerHTML = `
            <input type="checkbox" value="${airline}" class="airline-checkbox" ${isChecked ? "checked" : ""}>
            <span>${airline}</span>
        `;
        container.appendChild(label);
    });

    // Attach change listeners
    container.querySelectorAll(".airline-checkbox").forEach(cb => {
        cb.addEventListener("change", debouncedFilterUpdate);
    });
}

// Populate airline dropdown in manual review form
function populateManualAirlineSelect(allAirlines) {
    const select = document.getElementById("manualAirlineSelect");
    if (!select) return;
    select.innerHTML = "";
    allAirlines.forEach(air => {
        const opt = document.createElement("option");
        opt.value = air;
        opt.textContent = air;
        select.appendChild(opt);
    });
}

// =========================================================
// 4. CHART.JS CHARTS RENDERING & THEME SYNC
// =========================================================

// Chart 1: Overall Sentiment Distribution (Doughnut)
function renderDistributionChart(chartData) {
    const canvas = document.getElementById("chartDistribution");
    if (!canvas) return;
    const colors = getThemeColors();

    const dataConfig = {
        labels: chartData.labels,
        datasets: [{
            data: chartData.counts,
            backgroundColor: [colors.positive, colors.negative, colors.neutral],
            borderColor: colors.cardBg,
            borderWidth: 2,
            hoverOffset: 6,
        }]
    };

    if (chartDistInstance) {
        chartDistInstance.data = dataConfig;
        chartDistInstance.options.plugins.legend.labels.color = colors.text;
        chartDistInstance.update();
    } else {
        chartDistInstance = new Chart(canvas, {
            type: "doughnut",
            data: dataConfig,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                cutout: "62%",
                plugins: {
                    legend: {
                        position: "bottom",
                        labels: {
                            color: colors.text,
                            boxWidth: 12,
                            padding: 14,
                            font: { size: 11, weight: "600" }
                        }
                    },
                    tooltip: {
                        callbacks: {
                            label: function(ctx) {
                                const val = ctx.raw || 0;
                                const total = ctx.dataset.data.reduce((a, b) => a + b, 0);
                                const pct = total > 0 ? ((val / total) * 100).toFixed(1) : 0;
                                return ` ${ctx.label}: ${val} (${pct}%)`;
                            }
                        }
                    }
                }
            }
        });
    }
}

// Chart 2: Airline-wise Sentiment Comparison (Grouped Bar)
function renderAirlineComparisonChart(chartData) {
    const canvas = document.getElementById("chartAirlineComparison");
    if (!canvas) return;
    const colors = getThemeColors();

    const dataConfig = {
        labels: chartData.labels,
        datasets: [
            {
                label: "Positive",
                data: chartData.positive,
                backgroundColor: colors.positive,
                borderRadius: 4,
            },
            {
                label: "Negative",
                data: chartData.negative,
                backgroundColor: colors.negative,
                borderRadius: 4,
            },
            {
                label: "Neutral",
                data: chartData.neutral,
                backgroundColor: colors.neutral,
                borderRadius: 4,
            }
        ]
    };

    if (chartAirlineInstance) {
        chartAirlineInstance.data = dataConfig;
        chartAirlineInstance.options.scales.x.ticks.color = colors.text;
        chartAirlineInstance.options.scales.x.grid.color = colors.gridLine;
        chartAirlineInstance.options.scales.y.ticks.color = colors.secondaryText;
        chartAirlineInstance.options.scales.y.grid.color = colors.gridLine;
        chartAirlineInstance.options.plugins.legend.labels.color = colors.text;
        chartAirlineInstance.update();
    } else {
        chartAirlineInstance = new Chart(canvas, {
            type: "bar",
            data: dataConfig,
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: "top",
                        labels: {
                            color: colors.text,
                            boxWidth: 12,
                            padding: 12,
                            font: { size: 11, weight: "600" }
                        }
                    }
                },
                scales: {
                    x: {
                        ticks: { color: colors.text, font: { size: 11 } },
                        grid: { color: colors.gridLine, display: false }
                    },
                    y: {
                        ticks: { color: colors.secondaryText, stepSize: 1, precision: 0 },
                        grid: { color: colors.gridLine }
                    }
                }
            }
        });
    }
}

// ─────────────────────────────────────────────────────────────────────────────
// Chart 3: Review Sentiment Timeline — Scatter, Three Horizontal Sentiment Rows
// ─────────────────────────────────────────────────────────────────────────────
//
// Sentiment Y-position mapping:
//   Positive → Y = 2
//   Negative → Y = 1
//   Neutral  → Y = 0
//
// Each review is plotted as an individual scatter point along the chronological timeline.

function sentimentToY(s) {
    if (s === "Positive") return 2;
    if (s === "Negative") return 1;
    if (s === "Neutral")  return 0;
    return null;  // invalid — skip this point
}

function sentimentToColor(s, colors) {
    if (s === "Positive") return colors.positive;
    if (s === "Negative") return colors.negative;
    return colors.neutral;
}

// Convert a "YYYY-MM" or "YYYY-MM-DD" string to a UTC midnight timestamp (ms).
// Using UTC avoids timezone-shift surprises when Chart.js formats the tick label.
function dateStringToMs(dateStr) {
    if (!dateStr) return null;
    // Append "-01" if only YYYY-MM so Date.parse handles it as the 1st of the month
    const normalized = dateStr.length === 7 ? dateStr + "-01" : dateStr;
    const ms = Date.UTC(
        parseInt(normalized.slice(0, 4)),
        parseInt(normalized.slice(5, 7)) - 1,
        parseInt(normalized.slice(8, 10) || "01")
    );
    return isNaN(ms) ? null : ms;
}

function renderDateTrendChart(chartData) {
    const canvas = document.getElementById("chartDateTrend");
    if (!canvas) return;
    const colors = getThemeColors();
    const freq   = chartData.frequency || "monthly";
    const timeline = chartData.timeline || [];

    // ── Title ──────────────────────────────────────────────────────────────
    const titleEl = document.getElementById("dateTrendTitle");
    if (titleEl) {
        titleEl.textContent = freq === "monthly"
            ? "Review Sentiment Timeline (2020 – 2026) — Monthly View"
            : "Review Sentiment Timeline (2020 – 2026) — Daily View";
    }

    // ── Build scatter points ───────────────────────────────────────────────
    // Each valid review becomes one {x: timestamp_ms, y: 0|1|2} point.
    // Per-point backgroundColor array colors each dot by its sentiment.
    // pointStyle array lets us use "+" for Positive, "−" for Negative, "=" for Neutral
    // (Chart.js does not support arbitrary unicode pointStyle, so we keep circles and
    //  rely on colors + the Y-row position + legend for identification.)
    const scatterPoints    = [];
    const pointColors      = [];
    const pointLabels      = [];  // kept for tooltip
    const pointActualDates = [];  // kept for tooltip (exact date even in monthly view)

    // Track unique x values to build a clean sorted axis label array
    const uniqueXMs = new Set();

    timeline.forEach(function(item) {
        const y = sentimentToY(item.sentiment);
        if (y === null) return;  // unknown sentiment — skip safely

        const ms = dateStringToMs(item.date);
        if (ms === null) return;  // unparseable date — skip safely

        scatterPoints.push({ x: ms, y: y });
        pointColors.push(sentimentToColor(item.sentiment, colors));
        pointLabels.push(item.sentiment);
        pointActualDates.push(item.actual_date || item.date);
        uniqueXMs.add(ms);
    });

    // Sorted unique x-values for custom tick generation (linear axis)
    const sortedXMs = Array.from(uniqueXMs).sort(function(a, b) { return a - b; });

    // ── Tick formatter: ms → readable date string ──────────────────────────
    function formatXTick(msVal) {
        const d = new Date(msVal);
        const yr  = d.getUTCFullYear();
        const mon = String(d.getUTCMonth() + 1).padStart(2, "0");
        const day = String(d.getUTCDate()).padStart(2, "0");
        return freq === "monthly" ? `${yr}-${mon}` : `${yr}-${mon}-${day}`;
    }

    // ── Dataset ────────────────────────────────────────────────────────────
    const dataConfig = {
        datasets: [{
            label: "Reviews",
            data: scatterPoints,
            backgroundColor: pointColors,
            borderColor:      pointColors,     // border same as fill for solid dots
            borderWidth: 1,
            pointRadius: 7,
            pointHoverRadius: 10,
            pointStyle: "circle",
            showLine: false,                   // absolutely no connecting lines
        }]
    };

    // ── Always destroy & recreate to avoid stale scale/data state ──────────
    if (chartTrendInstance) {
        chartTrendInstance.destroy();
        chartTrendInstance = null;
    }

    // ── Empty-state: show a user-friendly message, skip chart creation ──────
    if (scatterPoints.length === 0) {
        const ctx = canvas.getContext("2d");
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.save();
        ctx.fillStyle = colors.secondaryText || "#778196";
        ctx.font = "14px sans-serif";
        ctx.textAlign = "center";
        ctx.fillText("No reviews match the active filters.", canvas.width / 2, canvas.height / 2);
        ctx.restore();
        return;
    }

    chartTrendInstance = new Chart(canvas, {
        type: "scatter",
        data: dataConfig,
        options: {
            responsive: true,
            maintainAspectRatio: false,
            animation: { duration: 300 },
            plugins: {
                // ── Custom legend: three static sentiment rows (not dataset-based) ──
                legend: {
                    position: "top",
                    labels: {
                        color: colors.text,
                        boxWidth: 12,
                        padding: 14,
                        font: { size: 11, weight: "600" },
                        // Generate three fixed legend entries with the correct colors
                        generateLabels: function() {
                            return [
                                { text: "Positive", fillStyle: colors.positive, strokeStyle: colors.positive, lineWidth: 1, hidden: false, datasetIndex: 0 },
                                { text: "Negative", fillStyle: colors.negative, strokeStyle: colors.negative, lineWidth: 1, hidden: false, datasetIndex: 0 },
                                { text: "Neutral",  fillStyle: colors.neutral,  strokeStyle: colors.neutral,  lineWidth: 1, hidden: false, datasetIndex: 0 },
                            ];
                        }
                    },
                    // Clicking legend does nothing (single dataset, colors are per-point)
                    onClick: function() {}
                },
                tooltip: {
                    callbacks: {
                        label: function(ctx) {
                            const i   = ctx.dataIndex;
                            const lbl = pointLabels[i]      || "Unknown";
                            const dt  = pointActualDates[i] || "";
                            return ` ${lbl}  |  ${dt}`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    type: "linear",
                    // Use only the actual review dates as tick positions (no interpolated gaps)
                    afterBuildTicks: function(axis) {
                        axis.ticks = sortedXMs.map(function(ms) { return { value: ms }; });
                    },
                    ticks: {
                        color: colors.text,
                        font: { size: 10 },
                        maxRotation: 45,
                        autoSkip: true,
                        maxTicksLimit: 20,
                        callback: function(val) { return formatXTick(val); }
                    },
                    grid: { color: colors.gridLine },
                    title: {
                        display: false
                    }
                },
                y: {
                    // Three fixed rows: 0 = Neutral, 1 = Negative, 2 = Positive
                    min: -0.6,
                    max: 2.6,
                    ticks: {
                        stepSize: 1,
                        color: colors.text,
                        font: { size: 11, weight: "600" },
                        callback: function(val) {
                            if (val === 2) return "✚ Positive";
                            if (val === 1) return "– Negative";
                            if (val === 0) return "= Neutral";
                            return "";          // hide 0.5, 1.5 etc.
                        }
                    },
                    // Subtle horizontal grid lines only at the three sentinel rows
                    grid: {
                        color: function(ctx) {
                            const v = ctx.tick.value;
                            if (v === 0 || v === 1 || v === 2) return colors.gridLine;
                            return "transparent";
                        }
                    }
                }
            }
        }
    });
}


// Update all charts theme colors when dark/light mode toggles
function updateAllChartThemes() {
    const colors = getThemeColors();
    if (chartDistInstance) {
        chartDistInstance.data.datasets[0].backgroundColor = [colors.positive, colors.negative, colors.neutral];
        chartDistInstance.data.datasets[0].borderColor = colors.cardBg;
        chartDistInstance.options.plugins.legend.labels.color = colors.text;
        chartDistInstance.update();
    }
    if (chartAirlineInstance) {
        chartAirlineInstance.data.datasets[0].backgroundColor = colors.positive;
        chartAirlineInstance.data.datasets[1].backgroundColor = colors.negative;
        chartAirlineInstance.data.datasets[2].backgroundColor = colors.neutral;
        chartAirlineInstance.options.scales.x.ticks.color = colors.text;
        chartAirlineInstance.options.scales.x.grid.color = colors.gridLine;
        chartAirlineInstance.options.scales.y.ticks.color = colors.secondaryText;
        chartAirlineInstance.options.scales.y.grid.color = colors.gridLine;
        chartAirlineInstance.options.plugins.legend.labels.color = colors.text;
        chartAirlineInstance.update();
    }
    if (chartTrendInstance) {
        // Chart 3 uses per-point backgroundColor arrays (one color per dot).
        // In-place patching of those arrays is complex — it's cleaner and correct
        // to simply destroy the instance and re-render with the new theme colors.
        // fetchDashboardData() will call renderDateTrendChart() which rebuilds everything.
        chartTrendInstance.destroy();
        chartTrendInstance = null;
        fetchDashboardData();  // re-render Chart 3 with updated theme colors
    }
}

// =========================================================
// 5. REVIEWS TABLE RENDERER & SEARCH FILTER
// =========================================================
function renderReviewsTable(reviews) {
    const tbody = document.getElementById("reviewsTableBody");
    const countBadge = document.getElementById("tableRecordCount");
    if (!tbody) return;

    if (countBadge) countBadge.textContent = `Showing ${reviews.length} reviews`;

    if (!reviews || reviews.length === 0) {
        tbody.innerHTML = `<tr><td colspan="5" class="empty-state">No reviews match the active filters.</td></tr>`;
        return;
    }

    tbody.innerHTML = reviews.map(r => {
        let badgeClass = "badge-neu";
        if (r.sentiment === "Positive") badgeClass = "badge-pos";
        else if (r.sentiment === "Negative") badgeClass = "badge-neg";

        const scoreFormatted = (r.compound_score >= 0 ? "+" : "") + Number(r.compound_score).toFixed(4);

        return `
            <tr>
                <td style="font-weight: 600; white-space: nowrap;">${escapeHtml(r.airline)}</td>
                <td style="white-space: nowrap; color: var(--secondary-text);">${escapeHtml(r.date)}</td>
                <td class="feedback-cell">${escapeHtml(r.feedback)}</td>
                <td><span class="kpi-badge ${badgeClass}">${escapeHtml(r.sentiment)}</span></td>
                <td class="score-cell">${scoreFormatted}</td>
            </tr>
        `;
    }).join("");
}

function escapeHtml(text) {
    const div = document.createElement("div");
    div.textContent = text || "";
    return div.innerHTML;
}

// Client-side instant table search
function initTableSearch() {
    const searchInput = document.getElementById("tableSearchInput");
    if (!searchInput) return;

    searchInput.addEventListener("input", (e) => {
        const query = e.target.value.toLowerCase().trim();
        if (!query) {
            renderReviewsTable(allReviewsCache);
            return;
        }

        const filtered = allReviewsCache.filter(r => 
            (r.airline && r.airline.toLowerCase().includes(query)) ||
            (r.feedback && r.feedback.toLowerCase().includes(query)) ||
            (r.sentiment && r.sentiment.toLowerCase().includes(query))
        );
        renderReviewsTable(filtered);
    });
}

// =========================================================
// 6. EVENT LISTENERS (UPLOAD, MANUAL ENTRY, RESET, ACCORDIONS)
// =========================================================
function initEventListeners() {
    // 1. Sidebar Filter Checkboxes & Dates
    document.querySelectorAll(".sentiment-checkbox").forEach(cb => {
        cb.addEventListener("change", debouncedFilterUpdate);
    });

    const startInput = document.getElementById("startDateInput");
    const endInput = document.getElementById("endDateInput");
    if (startInput) startInput.addEventListener("change", debouncedFilterUpdate);
    if (endInput) endInput.addEventListener("change", debouncedFilterUpdate);

    // 2. Trend Frequency Toggle (Monthly vs Daily)
    const btnMonthly = document.getElementById("btnFreqMonthly");
    const btnDaily = document.getElementById("btnFreqDaily");
    if (btnMonthly && btnDaily) {
        btnMonthly.addEventListener("click", () => {
            currentFreq = "monthly";
            btnMonthly.classList.add("active");
            btnDaily.classList.remove("active");
            debouncedFilterUpdate();
        });
        btnDaily.addEventListener("click", () => {
            currentFreq = "daily";
            btnDaily.classList.add("active");
            btnMonthly.classList.remove("active");
            debouncedFilterUpdate();
        });
    }

    // 3. Reset Filters
    const btnReset = document.getElementById("btnResetFilters");
    if (btnReset) {
        btnReset.addEventListener("click", () => {
            document.querySelectorAll(".airline-checkbox").forEach(cb => cb.checked = true);
            document.querySelectorAll(".sentiment-checkbox").forEach(cb => cb.checked = true);
            if (startInput) startInput.value = startInput.min;
            if (endInput) endInput.value = endInput.max;
            currentFreq = "monthly";
            if (btnMonthly) btnMonthly.classList.add("active");
            if (btnDaily) btnDaily.classList.remove("active");
            fetchDashboardData();
        });
    }

    // 4. Reload Sample Dataset
    const btnReload = document.getElementById("btnReloadSample");
    if (btnReload) {
        btnReload.addEventListener("click", async () => {
            try {
                btnReload.textContent = "⏳ Reloading...";
                const res = await fetch("/api/reset-sample", { method: "POST" });
                const json = await res.json();
                btnReload.textContent = "🔄 Reload Sample Dataset";
                if (json.status === "success") {
                    allAvailableAirlines = []; // Trigger fresh populate
                    fetchDashboardData(true);
                }
            } catch (err) {
                btnReload.textContent = "🔄 Reload Sample Dataset";
                alert("Failed to reload sample dataset: " + err.message);
            }
        });
    }

    // 5. CSV File Upload (Drag and drop or click)
    const dropzone = document.getElementById("uploadDropzone");
    const fileInput = document.getElementById("csvFileInput");
    const uploadFeedback = document.getElementById("uploadFeedback");

    if (dropzone && fileInput) {
        dropzone.addEventListener("click", () => fileInput.click());

        dropzone.addEventListener("dragover", (e) => {
            e.preventDefault();
            dropzone.classList.add("dragover");
        });

        dropzone.addEventListener("dragleave", () => {
            dropzone.classList.remove("dragover");
        });

        dropzone.addEventListener("drop", (e) => {
            e.preventDefault();
            dropzone.classList.remove("dragover");
            if (e.dataTransfer.files && e.dataTransfer.files[0]) {
                handleFileUpload(e.dataTransfer.files[0]);
            }
        });

        fileInput.addEventListener("change", (e) => {
            if (e.target.files && e.target.files[0]) {
                handleFileUpload(e.target.files[0]);
            }
        });
    }

    async function handleFileUpload(file) {
        const formData = new FormData();
        formData.append("file", file);

        uploadFeedback.style.display = "block";
        uploadFeedback.style.color = "var(--secondary-text)";
        uploadFeedback.textContent = "Uploading & analyzing reviews with VADER...";

        try {
            const res = await fetch("/api/upload", {
                method: "POST",
                body: formData
            });
            const json = await res.json();

            if (json.status === "success") {
                uploadFeedback.style.color = "var(--positive)";
                uploadFeedback.textContent = json.message;
                allAvailableAirlines = []; // Re-populate filters
                fetchDashboardData(true);
            } else {
                uploadFeedback.style.color = "var(--negative)";
                uploadFeedback.textContent = "Error: " + json.message;
            }
        } catch (err) {
            uploadFeedback.style.color = "var(--negative)";
            uploadFeedback.textContent = "Upload failed: " + err.message;
        }
    }

    // 6. Manual Review Entry Form
    const manualForm = document.getElementById("manualReviewForm");
    const manualAlert = document.getElementById("manualReviewAlert");

    if (manualForm) {
        // Set default review date to today
        const dateInput = document.getElementById("manualDateInput");
        if (dateInput) dateInput.value = new Date().toISOString().split("T")[0];

        manualForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const airline = document.getElementById("manualAirlineSelect").value;
            const date = document.getElementById("manualDateInput").value;
            const feedback = document.getElementById("manualFeedbackText").value;

            try {
                const res = await fetch("/api/reviews", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ airline, date, feedback })
                });
                const json = await res.json();

                if (json.status === "success") {
                    manualAlert.className = "form-alert success";
                    manualAlert.textContent = json.message;
                    document.getElementById("manualFeedbackText").value = "";
                    fetchDashboardData();
                } else {
                    manualAlert.className = "form-alert error";
                    manualAlert.textContent = json.message;
                }
            } catch (err) {
                manualAlert.className = "form-alert error";
                manualAlert.textContent = "Failed to submit review: " + err.message;
            }
        });
    }

    // 7. Accordions Toggle
    initAccordion("manualReviewAccordion", "manualAccordionHeader");
    initAccordion("methodologyAccordion", "methodologyAccordionHeader");

    // 8. Mobile Menu Toggle
    const mobileBtn = document.getElementById("mobileMenuBtn");
    const sidebar = document.getElementById("sidebar");
    if (mobileBtn && sidebar) {
        mobileBtn.addEventListener("click", () => {
            sidebar.classList.toggle("open");
        });
        // Click outside closes sidebar on mobile
        document.addEventListener("click", (e) => {
            if (sidebar.classList.contains("open") && !sidebar.contains(e.target) && e.target !== mobileBtn) {
                sidebar.classList.remove("open");
            }
        });
    }
}

function initAccordion(cardId, headerId) {
    const card = document.getElementById(cardId);
    const header = document.getElementById(headerId);
    if (card && header) {
        header.addEventListener("click", () => {
            card.classList.toggle("open");
        });
    }
}

// =========================================================
// 7. APPLICATION BOOTSTRAP
// =========================================================
document.addEventListener("DOMContentLoaded", () => {
    initTheme();
    initEventListeners();
    initTableSearch();
    fetchDashboardData(true);
});
