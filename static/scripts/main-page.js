document.addEventListener("DOMContentLoaded", function () {
    const urlInput = document.getElementById("url");
    const thumbnailContainer = document.getElementById("thumbnail-container");
    const thumbnail = document.getElementById("thumbnail");
    const errorMsg = document.getElementById("error-msg");
    const downloadForm = document.getElementById("download-form");
    const toastMessage = document.getElementById("toast-message");
    const toastElement = document.getElementById("toast");
    const darkModeToggle = document.getElementById("toggle-dark-mode");
    const themeStyle = document.getElementById("theme-style");

    // Theme URLs from data attributes
    const lightTheme = darkModeToggle.dataset.light;
    const darkTheme = darkModeToggle.dataset.dark;

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
            showToast("Download complete!");
        }
    });

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

    function showError() {
        errorMsg.classList.remove("d-none");
    }

    function hideError() {
        errorMsg.classList.add("d-none");
    }

    function getYouTubeVideoId(url) {
        const match = url.match(/(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([^"&?\/\s]{11})/);
        return match ? match[1] : null;
    }

    function showToast(message) {
        toastMessage.innerText = message;
        const toast = new bootstrap.Toast(toastElement);
        toast.show();
    }
});
