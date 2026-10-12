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

// Chart 3: Date-wise Sentiment Trend (Line)
function renderDateTrendChart(chartData) {
    const canvas = document.getElementById("chartDateTrend");
    if (!canvas) return;
    const colors = getThemeColors();

    const titleEl = document.getElementById("dateTrendTitle");
    if (titleEl) {
        titleEl.textContent = chartData.frequency === "monthly" 
            ? "Chart 3: Monthly Sentiment Trend (Actual Review Months, 2020 – 2026)"
            : "Chart 3: Daily Sentiment Observations (2020 – 2026)";
    }

    const dataConfig = {
        labels: chartData.labels,
        datasets: [
            {
                label: "Positive",
                data: chartData.positive,
                borderColor: colors.positive,
                backgroundColor: colors.positive,
                tension: 0.25,
                borderWidth: 2.2,
                pointRadius: 4,
                pointHoverRadius: 6,
            },
            {
                label: "Negative",
                data: chartData.negative,
                borderColor: colors.negative,
                backgroundColor: colors.negative,
                tension: 0.25,
                borderWidth: 2.2,
                pointRadius: 4,
                pointHoverRadius: 6,
            },
            {
                label: "Neutral",
                data: chartData.neutral,
                borderColor: colors.neutral,
                backgroundColor: colors.neutral,
                tension: 0.25,
                borderWidth: 2.2,
                pointRadius: 4,
                pointHoverRadius: 6,
            }
        ]
    };

    if (chartTrendInstance) {
        chartTrendInstance.data = dataConfig;
        chartTrendInstance.options.scales.x.ticks.color = colors.text;
        chartTrendInstance.options.scales.x.grid.color = colors.gridLine;
        chartTrendInstance.options.scales.y.ticks.color = colors.secondaryText;
        chartTrendInstance.options.scales.y.grid.color = colors.gridLine;
        chartTrendInstance.options.plugins.legend.labels.color = colors.text;
        chartTrendInstance.update();
    } else {
        chartTrendInstance = new Chart(canvas, {
            type: "line",
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
                        ticks: { color: colors.text, font: { size: 10 }, maxRotation: 45 },
                        grid: { color: colors.gridLine }
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
        chartTrendInstance.data.datasets[0].borderColor = colors.positive;
        chartTrendInstance.data.datasets[0].backgroundColor = colors.positive;
        chartTrendInstance.data.datasets[1].borderColor = colors.negative;
        chartTrendInstance.data.datasets[1].backgroundColor = colors.negative;
        chartTrendInstance.data.datasets[2].borderColor = colors.neutral;
        chartTrendInstance.data.datasets[2].backgroundColor = colors.neutral;
        chartTrendInstance.options.scales.x.ticks.color = colors.text;
        chartTrendInstance.options.scales.x.grid.color = colors.gridLine;
        chartTrendInstance.options.scales.y.ticks.color = colors.secondaryText;
        chartTrendInstance.options.scales.y.grid.color = colors.gridLine;
        chartTrendInstance.options.plugins.legend.labels.color = colors.text;
        chartTrendInstance.update();
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
