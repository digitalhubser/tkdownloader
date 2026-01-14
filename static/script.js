    let currentTaskId = null;

    async function startDownload() {
        const url = document.getElementById('videoUrl').value;
        const quality = document.getElementById('videoQuality').value;
        const statusBox = document.getElementById('statusBox');
        const startBtn = document.getElementById('startBtn');
        
        if (!url) {
            alert("يرجى إدخال رابط صحيح");
            return;
        }

        // تحضير الواجهة
        startBtn.disabled = true;
        statusBox.innerHTML = '<div class="loading-spinner"></div><p>جاري التواصل مع السيرفر والتحميل من يوتيوب...</p>';
        
        try {
            const response = await fetch('/download', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ url: url, quality: quality })
            });
            
            const data = await response.json();
            currentTaskId = data.task_id;
            checkStatus();
        } catch (error) {
            statusBox.innerText = "فشل الاتصال بالسيرفر.";
            startBtn.disabled = false;
        }
    }

    async function checkStatus() {
        if (!currentTaskId) return;

        const response = await fetch('/status/' + currentTaskId);
        const data = await response.json();
        const statusBox = document.getElementById('statusBox');
        const startBtn = document.getElementById('startBtn');

        if (data.status === 'downloading') {
            setTimeout(checkStatus, 3000); // تحديث كل 3 ثواني
        } 
        else if (data.status === 'finished') {
            statusBox.innerHTML = `
                <p style="color: green; font-weight: bold;">✅ اكتملت العملية!</p>
                <a href="/download_file/${data.file}" class="download-btn">تحميل الملف المضغوط (ZIP)</a>
            `;
            startBtn.disabled = false;
        } 
        else if (data.status === 'fallback') {
            statusBox.innerHTML = `
                <div class="warning-text">⚠️ تعذر إنشاء ملف مضغوط واحد. يمكنك تحميل الفيديوهات بشكل منفصل أدناه:</div>
            `;
            data.files.forEach(fileName => {
                const link = document.createElement("a");
                link.href = `/download_single/${currentTaskId}/${fileName}`;
                link.className = "single-download-link";
                link.innerText = "⬇️ تحميل: " + fileName;
                statusBox.appendChild(link);
            });
            startBtn.disabled = false;
        } 
        else if (data.status === 'failed') {
            statusBox.innerHTML = `<p style="color: red;">❌ الرابط غير صحيح : </p>`;
            startBtn.disabled = false;
        }
    }
    
    // ${data.error}