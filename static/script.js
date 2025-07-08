// ======= Auto scroll on new message =======
const chatBox = document.getElementById("main-box");
function scrollToBottom() {
    chatBox.scrollTop = chatBox.scrollHeight;
}
window.onload = scrollToBottom;
new MutationObserver(scrollToBottom).observe(chatBox, { childList: true, subtree: true });

// ======= Sidebar toggle =======
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

// ======= Toggle Upload Box =======
document.getElementById('showupload').addEventListener('click', () => {
    document.getElementById('uploadBox').classList.toggle('hidden');
});

// ======= Append Message to Chatbox =======
function appendToChatBox(role, message) {
    const msg = document.createElement("p");
    msg.className = "text-base my-2";
    msg.innerHTML = `<strong>${role}:</strong> ${message}`;
    chatBox.appendChild(msg);
    scrollToBottom();
    return msg;
}

// ======= Load Files on Page Load =======
async function loadExistingFiles() {
    try {
        const response = await fetch("/list-files");
        const files = await response.json();
        const fileList = document.getElementById("file-list");
        fileList.innerHTML = "";
        files.forEach(filename => {
            const li = createFileCard(filename);
            fileList.appendChild(li);
        });
    } catch (error) {
        console.error("Failed to load files:", error);
    }
}
window.addEventListener("load", () => {
    scrollToBottom();
    loadExistingFiles();
});

// ======= File Card Generator =======
function createFileCard(filename) {
    const li = document.createElement("li");
    li.classList.add("bg-white", "rounded-lg", "shadow", "p-2", "flex", "items-center", "space-x-3", "text-black");

    const img = document.createElement("img");
    img.src = "/static/pdf-icon.png";
    img.onerror = () => img.src = "https://cdn-icons-png.flaticon.com/512/337/337946.png";
    img.alt = "PDF";
    img.classList.add("w-10", "h-10", "object-contain");

    const name = document.createElement("a");
    name.href = `/uploads/${filename}`;
    name.textContent = filename;
    name.target = "_blank";
    name.classList.add("flex-1", "truncate", "hover:underline");

    const deleteBtn = document.createElement("button");
    deleteBtn.innerHTML = `<i class="fa-solid fa-trash text-red-600 hover:text-red-800"></i>`;
    deleteBtn.title = "Delete file";
    deleteBtn.onclick = async () => {
        if (confirm(`Delete "${filename}"?`)) {
            const res = await fetch(`/delete-file/${filename}`, { method: "DELETE" });
            if (res.ok) {
                li.remove();
                const currentFilename = document.getElementById("filename")?.textContent.trim();
                if (currentFilename === filename) {
                    document.getElementById("filename").textContent = "";
                    document.getElementById("result").style.display = "none";
                }
            } else {
                alert("Failed to delete file.");
            }
        }
    };

    li.appendChild(img);
    li.appendChild(name);
    li.appendChild(deleteBtn);
    return li;
}

// ======= Upload Form Handler =======
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

        let result = await response.json();

        if (response.ok && result.filename) {
            document.getElementById("filename").textContent = result.filename;
            document.getElementById("result").style.display = "block";
            fileInput.value = "";

            const li = createFileCard(result.filename);
            document.getElementById("file-list").appendChild(li);

            // Auto summary
            appendToChatBox("System", "📄 Summarizing document...");
            const summaryMsg = appendToChatBox("Summary", "⏳ Generating summary...");

            try {
                const summaryRes = await fetch(`/summarize/${result.filename}`);
                const summaryData = await summaryRes.json();
                summaryMsg.innerHTML = `<strong>Summary:</strong> ${summaryData.summary || "⚠️ No summary available."}`;
            } catch (err) {
                summaryMsg.innerHTML = `<strong>Summary:</strong> ⚠️ Error generating summary.`;
                console.error("Summary error:", err);
            }

        } else {
            alert(result.error || "Upload failed.");
        }

    } catch (err) {
        console.error("Upload error:", err);
        alert("Something went wrong. Please try again.");
    }
});

// ======= Ask Question Form Handler =======
document.getElementById("question-form").addEventListener("submit", async (e) => {
    e.preventDefault();
    const input = document.querySelector("input[name='queryText']");
    const question = input.value.trim();
    const filename = document.getElementById("filename")?.textContent.trim();

    if (!question || !filename) {
        alert("❗ Please upload a PDF and enter a question.");
        return;
    }

    appendToChatBox("You", question);
    input.value = "";

    try {
        const res = await fetch("/ask", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ question, filename })
        });

        const data = await res.json();

        appendToChatBox("ASK", data.answer || "❌ No answer received.");
        if (data.source) appendToChatBox("📄 Source", data.source);

    } catch (err) {
        console.error("Error:", err);
        appendToChatBox("ASK", "⚠️ Failed to fetch answer.");
    }
});

// ======= Profile dropdown toggle =======
document.querySelector("#profileIcon").addEventListener("click", () => {
    document.querySelector("#myAccountBox").classList.toggle("hidden");
});

// ======= Login/Signup toggle =======
document.getElementById("ci1").onclick = () => document.getElementById("loginPage").style.display = "none";
document.getElementById("ci2").onclick = () => document.getElementById("loginPage").style.display = "none";

document.getElementById("su").onclick = () => {
    document.getElementById("loginBox").style.display = "none";
    document.getElementById("signupBox").style.display = "block";
};
document.getElementById("si").onclick = () => {
    document.getElementById("signupBox").style.display = "none";
    document.getElementById("loginBox").style.display = "block";
};

// ======= Signup Submit Handler =======
document.getElementById("signupSubmit").addEventListener("click", function (e) {
    e.preventDefault();

    const email = document.getElementById("signupEmail").value;
    const pass = document.getElementById("signupPass").value;
    const profile = document.querySelector('input[name="pp"]:checked')?.value;

    const formData = new FormData();
    formData.append("email", email);
    formData.append("pass", pass);
    formData.append("pp", profile);

    fetch("/signup_req", {
        method: "POST",
        body: formData
    })
    .then(res => res.json())
    .then(data => {
        const msg = document.getElementById("signup-message");
        msg.classList.remove("bg-red-500", "bg-green-500", "text-white", "hidden");

        if (data.status === "success") {
            msg.innerText = "✅ Account created! Please log in.";
            setTimeout(() => {
                msg.innerText = "";
                msg.classList.add("hidden");
                document.getElementById("signup").reset();
                document.getElementById("signupBox").classList.add("hidden");
                document.getElementById("loginBox").classList.remove("hidden");
            }, 2000);
        } else {
            msg.innerText = data.message || "❌ This account already exists.";
            document.getElementById("signupPass").value = "";
            setTimeout(() => msg.classList.add("hidden"), 2000);
        }
    })
    .catch(err => {
        console.error(err);
        const msg = document.getElementById("signup-message");
        msg.innerText = "⚠️ Server error. Try again.";
        msg.classList.add("bg-red-500", "text-white");
        setTimeout(() => msg.classList.add("hidden"), 2000);
    });
});
