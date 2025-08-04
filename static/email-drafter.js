document.getElementById("emailForm").addEventListener("submit", async function (e) {
    e.preventDefault();

    const data = {
        emailType: document.getElementById("emailType").value,
        recipientType: document.getElementById("recipientType").value,
        tone: document.getElementById("emailTone").value,
        purpose: document.getElementById("emailPurpose").value,
        context: document.getElementById("emailContext").value,
        senderName: document.getElementById("senderName").value,
    };

    const preview = document.getElementById("emailPreview");
    const generateBtn = document.getElementById("generateBtn");
    const copyBtn = document.getElementById("copyEmailBtn");
    const downloadBtn = document.getElementById("downloadBtn");

    preview.innerHTML = "<p class='text-muted'>Generating email...</p>";
    generateBtn.disabled = true;

    try {
        const response = await fetch("/api/draft-email", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data),
        });

        const result = await response.json();
        if (result.subject && result.body) {
            preview.innerHTML = `
                <strong>Subject:</strong> ${result.subject}<br><br>
                ${result.body}<br><br>
                <em>${result.signature}</em>
            `;
            copyBtn.style.display = "inline-block";
            downloadBtn.style.display = "inline-block";

            // Attach download
            downloadBtn.onclick = () => {
                const blob = new Blob(
                    [`Subject: ${result.subject}\n\n${result.body}\n\n${result.signature}`],
                    { type: "text/plain;charset=utf-8" }
                );
                const url = URL.createObjectURL(blob);
                const a = document.createElement("a");
                a.href = url;
                a.download = "drafted_email.txt";
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
            };

            // Attach copy
            copyBtn.onclick = () => {
                navigator.clipboard.writeText(`${result.subject}\n\n${result.body}\n\n${result.signature}`);
                copyBtn.innerHTML = "<i class='fas fa-check me-1'></i>Copied!";
                setTimeout(() => copyBtn.innerHTML = "<i class='fas fa-copy me-1'></i>Copy Email", 1500);
            };
        } else {
            preview.innerHTML = "<p class='text-danger'>Failed to generate email. Try again later.</p>";
        }
    } catch (error) {
        console.error(error);
        preview.innerHTML = "<p class='text-danger'>Server error. Please try again.</p>";
    } finally {
        generateBtn.disabled = false;
    }
});
