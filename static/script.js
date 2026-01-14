document.getElementById('downloadBtn').addEventListener('click', async () => {
    const url = document.getElementById('videoUrl').value;
    const quality = document.getElementById('quality').value;
    const statusDiv = document.getElementById('status');

    if (!url) {
        statusDiv.innerText = "الرجاء إدخال الرابط أولاً!";
        statusDiv.style.color = "red";
        return;
    }

    statusDiv.innerText = "جاري الاتصال بالسيرفر والتحميل...";
    statusDiv.style.color = "blue";

    try {
        const response = await fetch('/download', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ url: url, quality: quality })
        });

        const data = await response.json();

        if (response.ok) {
            statusDiv.style.color = "green";
            statusDiv.innerText = data.message;
        } else {
            statusDiv.style.color = "red";
            statusDiv.innerText = "خطأ: " + data.error;
        }
    } catch (err) {
        statusDiv.style.color = "red";
        statusDiv.innerText = "فشل الاتصال بالسيرفر!";
    }
});
