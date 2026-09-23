from flask import Flask, render_template, request, send_file
import yt_dlp
import os

app = Flask(__name__)

# İndirilen videoların geçici olarak saklanacağı klasör
DOWNLOAD_FOLDER = 'downloads'
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    url = request.form.get('url')
    download_type = request.form.get('type') # 'video' veya 'audio'

    if not url:
        return "Geçerli bir link girmediniz!", 400

    ydl_opts = {
        'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
    }

    if download_type == 'audio':
        ydl_opts.update({
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        })
    else:
        ydl_opts.update({
            'format': 'best',
        })

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
            if download_type == 'audio':
                filename = os.path.splitext(filename)[0] + '.mp3'
                
        return send_file(filename, as_attachment=True)
    
    except Exception as e:
        return f"Bir hata oluştu: {str(e)}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)