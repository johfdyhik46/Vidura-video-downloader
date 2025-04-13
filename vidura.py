from flask import Flask, request, send_file, render_template_string
import yt_dlp
import os
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.DEBUG)

@app.route('/')
def index():
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Vidura - Video Downloader</title>
        <link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
        <style>
            body { background: linear-gradient(to bottom, #1e3a8a, #3b82f6); min-height: 100vh; }
            .loader { display: none; border: 8px solid #f3f3f3; border-top: 8px solid #3b82f6; border-radius: 50%; width: 40px; height: 40px; animation: spin 1s linear infinite; margin: auto; }
            @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }
            .error { color: #dc2626; font-weight: bold; }
            .success { color: #16a34a; font-weight: bold; }
            .input-container { position: relative; }
            .input-container svg { position: absolute; right: 10px; top: 50%; transform: translateY(-50%); }
        </style>
    </head>
    <body class="flex items-center justify-center px-4">
        <div class="bg-white p-6 md:p-8 rounded-xl shadow-2xl w-full max-w-lg">
            <h1 class="text-3xl font-extrabold text-center text-gray-800 mb-3">Vidura Downloader</h1>
            <p class="text-center text-gray-500 mb-6">Download videos from YouTube, Facebook, Instagram, and more</p>
            <form id="download-form" method="POST" action="/download" class="space-y-4">
                <div class="input-container">
                    <input type="url" name="url" id="url-input" placeholder="Paste video URL here" class="w-full p-3 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500" required>
                    <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l-4 4a4 4 0 00-5.656-5.656l-1.1 1.1" />
                    </svg>
                </div>
                <button type="submit" id="download-btn" class="w-full bg-blue-600 text-white p-3 rounded-lg hover:bg-blue-700 transition font-semibold">Download Now</button>
            </form>
            <div id="loader" class="loader mt-4"></div>
            <p id="message" class="mt-4 text-center"></p>
            <div class="mt-6 text-center">
                <div id="ad-container" class="bg-gray-100 p-4 rounded-lg">
                    <p class="text-gray-500">Ad Space</p>
                </div>
            </div>
        </div>
        <script>
            const form = document.getElementById('download-form');
            const loader = document.getElementById('loader');
            const message = document.getElementById('message');
            const button = document.getElementById('download-btn');

            form.addEventListener('submit', async (e) => {
                e.preventDefault();
                loader.style.display = 'block';
                message.textContent = '';
                button.disabled = true;

                const url = document.getElementById('url-input').value;
                try {
                    const response = await fetch('/download', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                        body: `url=${encodeURIComponent(url)}`
                    });

                    loader.style.display = 'none';
                    button.disabled = false;

                    if (response.ok) {
                        const blob = await response.blob();
                        const link = document.createElement('a');
                        link.href = URL.createObjectURL(blob);
                        link.download = 'video.mp4';
                        link.click();
                        message.textContent = 'Download started!';
                        message.className = 'success';
                    } else {
                        const error = await response.text();
                        throw new Error(error);
                    }
                } catch (err) {
                    loader.style.display = 'none';
                    button.disabled = false;
                    message.textContent = err.message || 'Something went wrong. Try again!';
                    message.className = 'error';
                }
            });
        </script>
    </body>
    </html>
    ''')

@app.route('/download', methods=['POST'])
def download():
    url = request.form['url']
    ydl_opts = {
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'noplaylist': True,
        'quiet': True,
        'format': 'best[filesize<50M]',  # Use best single stream, no merging
    }
    filename = None
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
        if not os.path.exists(filename):
            raise FileNotFoundError("Downloaded file not found")
        return send_file(filename, as_attachment=True)
    except Exception as e:
        app.logger.error(f"Download error: {str(e)}")
        return f"Failed to download: {str(e)}", 500
    finally:
        if filename and os.path.exists(filename):
            try:
                os.remove(filename)
            except Exception as e:
                app.logger.error(f"Cleanup error: {str(e)}")

if __name__ == '__main__':
    os.makedirs('downloads', exist_ok=True)
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
