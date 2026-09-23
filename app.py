from flask import Flask, render_template, request, jsonify
import os
import re
import yt_dlp

app = Flask(__name__)
DOWNLOAD_FOLDER = r'D:\IndirilenVideolar'

if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

# İlerleme bilgilerini saklamak için sözlük
download_progress = {'percent': '0%', 'downloaded': '0 MB', 'total': '0 MB'}

def my_hook(d):
    if d['status'] == 'downloading':
        # Yüzde bilgisini alıp renk kodlarından (ANSI escape codes) tamamen temizliyoruz
        raw_p = d.get('_percent_str', '0%')
        p_clean = re.sub(r'\x1b\[[0-9;]*m', '', raw_p).strip()
        download_progress['percent'] = p_clean
        
        # İndirilen ve toplam boyut bilgileri (Byte cinsinden MB'a çevirme)
        downloaded_bytes = d.get('downloaded_bytes', 0)
        total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
        
        downloaded_mb = f"{downloaded_bytes / (1024 * 1024):.1f} MB"
        total_mb = f"{total_bytes / (1024 * 1024):.1f} MB" if total_bytes > 0 else "Bilinmiyor"
        
        download_progress['downloaded'] = downloaded_mb
        download_progress['total'] = total_mb

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/progress')
def progress():
    return jsonify(download_progress)

@app.route('/download', methods=['POST'])
def download():
    data = request.json
    url = data.get('url')
    dl_type = data.get('type')

    if not url:
        return jsonify({'success': False, 'error': 'Geçerli bir bağlantı girilmedi!'})

    download_progress['percent'] = '0%'
    download_progress['downloaded'] = '0 MB'
    download_progress['total'] = '0 MB'

    ydl_opts = {
        'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
        'progress_hooks': [my_hook],
    }

    if dl_type == 'audio':
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
            'format': 'bestvideo+bestaudio/best',
            'merge_output_format': 'mp4',
        })

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            if dl_type == 'audio':
                filename = os.path.splitext(filename)[0] + '.mp3'
            else:
                filename = os.path.splitext(filename)[0] + '.mp4'
            
        return jsonify({'success': True, 'filename': os.path.basename(filename)})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True, port=5000)