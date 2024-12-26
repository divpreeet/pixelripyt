document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('convertForm');
    const statusMessage = document.getElementById('statusMessage');
    const downloadContainer = document.getElementById('downloadContainer');
    const downloadLink = document.getElementById('downloadLink');
    const videoInfo = document.getElementById('videoInfo');

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        const formData = new FormData(form);
        
        // Show status message and reset other elements
        statusMessage.style.display = 'block';
        statusMessage.textContent = 'Fetching video information...';
        downloadContainer.style.display = 'none';
        videoInfo.innerHTML = '';

        try {
            const infoResponse = await fetch('/video_info', {
                method: 'POST',
                body: formData
            });

            if (infoResponse.ok) {
                const info = await infoResponse.json();
                videoInfo.innerHTML = `
                    <p><strong>Title:</strong> ${info.title}</p>
                    <p><strong>Duration:</strong> ${info.duration}</p>
                    <p><strong>Views:</strong> ${info.views}</p>
                `;
                statusMessage.textContent = 'Starting conversion...';
            }

            const response = await fetch('/convert', {
                method: 'POST',
                body: formData
            });

            if (response.ok) {
                const contentDisposition = response.headers.get('Content-Disposition');
                const filenameMatch = contentDisposition && contentDisposition.match(/filename="?(.+)"?/i);
                const filename = filenameMatch ? filenameMatch[1] : 'download';

                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);
                
                downloadLink.href = url;
                downloadLink.download = filename;
                downloadLink.textContent = `Download`;
                
                downloadContainer.style.display = 'block';
                statusMessage.textContent = 'Conversion complete! Click the button below to download.';
            } else {
                throw new Error('Conversion failed');
            }
        } catch (error) {
            console.error('Error:', error);
            statusMessage.textContent = 'An error occurred. Please try again.';
            downloadContainer.style.display = 'none';
        }
    });
});


