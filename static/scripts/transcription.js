document.addEventListener("DOMContentLoaded", function () {
    const downloadForm = document.getElementById("download-form");
    const toastMessage = document.getElementById("toast-message");
    const toastElement = document.getElementById("toast");

    const loadingSpinner = document.getElementById("loading-spinner");
    const transcriptionForm = document.getElementById("transcription-form");
    const darkModeToggle = document.getElementById("toggle-dark-mode");
    const themeStyle = document.getElementById("theme-style");

    // Theme URLs from data attributes
    const lightTheme = darkModeToggle.dataset.light;
    const darkTheme = darkModeToggle.dataset.dark;


    if (transcriptionForm && loadingSpinner) {
        transcriptionForm.addEventListener('submit', function () {
            loadingSpinner.classList.remove('d-none');
        });
    }

    darkModeToggle.addEventListener("click", toggleDarkMode);

    if (localStorage.getItem("dark-mode") === "enabled") {
        enableDarkMode();
    }

    function toggleDarkMode() {
        if (themeStyle.getAttribute("href") === lightTheme) {
            enableDarkMode();
        } else {
            enableLightMode();
        }
    }

    function enableDarkMode() {
        themeStyle.href = darkTheme;
        darkModeToggle.innerHTML = "☀️";
        localStorage.setItem("dark-mode", "enabled");
    }

    function enableLightMode() {
        themeStyle.href = lightTheme;
        darkModeToggle.innerHTML = "🌙";
        localStorage.setItem("dark-mode", "disabled");
    }

    document.getElementById("copy-button").addEventListener("click", function () {
        const textElement = document.getElementById("transcript-text");
        const transcriptText = textElement.innerText || textElement.textContent;
    
        navigator.clipboard.writeText(transcriptText)
            .then(() => showToast("Transcript copied to clipboard!"))
            .catch(err => alert("Failed to copy transcript."));
    });

    document.getElementById("download-form").addEventListener("submit", function (e) {
        e.preventDefault(); // Empêche le reload
        const form = this;
        const url = form.url.value.trim();
        const spinner = document.getElementById("loading-spinner");
        const errorMsg = document.getElementById("error-msg");
    
        errorMsg.classList.add("d-none");
        spinner.classList.remove("d-none");
    
        fetch("/", {
            method: "POST",
            headers: {
                "Content-Type": "application/x-www-form-urlencoded"
            },
            body: new URLSearchParams({ url: url })
        })
        .then(async (response) => {
            spinner.classList.add("d-none");
            if (!response.ok) {
                errorMsg.classList.remove("d-none");
                return;
            }
    
            const blob = await response.blob();
            const contentDisposition = response.headers.get("Content-Disposition");
            const fileName = contentDisposition?.match(/filename="(.+)"/)?.[1] || "video.mp4";
    
            const link = document.createElement("a");
            link.href = window.URL.createObjectURL(blob);
            link.download = fileName;
            link.click();
        })
        .catch(() => {
            spinner.classList.add("d-none");
            errorMsg.classList.remove("d-none");
        });
    });

    urlInput.addEventListener("input", function () {
        const url = this.value;
        const videoId = getYouTubeVideoId(url);

        if (videoId) {
            thumbnail.src = `https://img.youtube.com/vi/${videoId}/hqdefault.jpg`;
            thumbnailContainer.style.display = "block";
            hideError();
        } else {
            thumbnailContainer.style.display = "none";
            showError();
        }
    });

    downloadForm.addEventListener("submit", function (event) {
        const url = urlInput.value;
        if (!getYouTubeVideoId(url)) {
            showError();
            event.preventDefault();
        } else {
            hideError();
        }
    });

    function showToast(message) {
        toastMessage.innerText = message;
        const toast = new bootstrap.Toast(toastElement);
        toast.show();
    }


});