// Auto scroll to bottom
const chatBox = document.getElementById("main-box");
function scrollToBottom() {
    chatBox.scrollTop = chatBox.scrollHeight;
}
window.onload = scrollToBottom;
new MutationObserver(scrollToBottom).observe(chatBox, { childList: true, subtree: true });

// Toggle upload box
const toggleBtn = document.getElementById('showupload');
const uploadBox = document.getElementById('uploadBox');
toggleBtn.addEventListener('click', () => {
    uploadBox.classList.toggle('hidden');
});

// Sidebar toggle with smooth transition
const sidebutton = document.querySelector("#sidebar");
const leftside = document.querySelector("#left-side");
const rightside = document.querySelector("#right-side");
let flag = 0;
sidebutton.addEventListener('click', () => {
    leftside.style.transition = "width 0.3s ease";
    rightside.style.transition = "width 0.3s ease";

    if (flag === 0) {
        leftside.style.display = "block";
        setTimeout(() => {
            leftside.style.width = "25%";
            rightside.style.width = "75%";
        }, 10);
        flag = 1;
    } else {
        leftside.style.width = "0%";
        rightside.style.width = "100%";
        setTimeout(() => {
            leftside.style.display = "none";
        }, 300);
        flag = 0;
    }
});

// Handle file upload
document.getElementById("upload-form").addEventListener("submit", async function (e) {
    e.preventDefault();
    const fileInput = document.getElementById("pdf-file");
    const file = fileInput.files[0];
    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    try {
        const response = await fetch("/upload", {
            method: "POST",
            body: formData
        });
        const result = await response.json();

        if (response.ok) {
            // Show file summary below upload form
            document.getElementById("filename").textContent = result.filename;
            document.getElementById("filename").style.height = "auto";
            document.getElementById("result").style.display = "block";
            fileInput.value = "";

            // Add new file link to sidebar
            const fileList = document.getElementById("file-list");
            const li = document.createElement("li");
            const link = document.createElement("a");

            link.href = `/uploads/${result.filename}`;
            link.textContent = result.filename;
            link.target = "_blank"; // Opens in new tab
            link.classList.add("block", "bg-pink-700", "p-2", "rounded", "hover:bg-pink-600", "transition", "duration-300");

            li.appendChild(link);
            fileList.appendChild(li);
        } else {
            alert(result.error || "Upload failed.");
        }
    } catch (err) {
        console.error("Fetch failed:", err);
        alert("An error occurred while uploading.");
    }
});


// Load existing files when page loads
async function loadExistingFiles() {
    try {
        const response = await fetch("/list-files");
        const files = await response.json();
        const fileList = document.getElementById("file-list");

        fileList.innerHTML = ""; // clear old list

        files.forEach(filename => {
            const li = document.createElement("li");
            const link = document.createElement("a");

            link.href = `/uploads/${filename}`;
            link.textContent = filename;
            link.target = "_blank";
            link.classList.add("block", "bg-pink-700", "p-2", "rounded", "hover:bg-pink-600", "transition", "duration-300");

            li.appendChild(link);
            fileList.appendChild(li);
        });
    } catch (error) {
        console.error("Failed to load existing files:", error);
    }
}

// Ensure it runs on page load
window.addEventListener("load", () => {
    scrollToBottom();
    loadExistingFiles();
});

