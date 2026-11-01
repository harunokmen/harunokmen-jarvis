"""Yerel Turkce sesli komut asistani. Keyfi kabuk komutu calistirmaz."""
import argparse
import datetime as dt
import json
import os
from pathlib import Path
import queue
import re
import subprocess
import sys
import unicodedata

ROOT = Path(__file__).resolve().parent

def normalize(text):
    text = text.lower().replace('ı', 'i')
    return ' '.join(''.join(c for c in unicodedata.normalize('NFKD', text)
                            if not unicodedata.combining(c)).split())

ACTIONS = {
    'saat kac': 'time', 'tarih ne': 'date', 'sistem durumu': 'status',
    'not defteri ac': 'notepad', 'hesap makinesi ac': 'calculator',
    'tarayici ac': 'browser', 'gorev yoneticisi ac': 'tasks',
    'performans raporu': 'report', 'yardim': 'help', 'dinlemeyi durdur': 'exit',
}

def resolve(text, voice=False):
    text = normalize(text)
    if voice:
        # Uyandirma kelimesi ayni cumlede bulunmali; rastgele konusma islenmez.
        match = re.fullmatch(r'(?:jarvis|jervis|carvis) (.+)', text)
        if not match:
            return None
        text = match.group(1)
    return ACTIONS.get(text)

class Assistant:
    def __init__(self, speak=True):
        self.engine = None
        if speak:
            try:
                import pyttsx3
                self.engine = pyttsx3.init()
                for voice in self.engine.getProperty('voices'):
                    if any(s in str(voice).lower() for s in ('turkish', 'tolga', 'tr-tr')):
                        self.engine.setProperty('voice', voice.id)
                        break
                self.engine.setProperty('rate', 165)
            except Exception as exc:
                print('Sesli yanit kullanilamiyor:', exc)

    def reply(self, message):
        print('Jarvis:', message, flush=True)
        if self.engine:
            try:
                self.engine.say(message)
                self.engine.runAndWait()
            except Exception:
                self.engine = None

    def execute(self, action, approved=False):
        if action not in set(ACTIONS.values()):
            self.reply('Komut izin listesinde değil.')
            return True
        if action in {'notepad', 'calculator', 'tasks', 'browser', 'report'} and not approved:
            self.reply('Bu işlem arayüzden açık onay gerektiriyor.')
            return True
        if action == 'exit':
            self.reply('Dinleme durduruldu.')
            return False
        if action == 'time':
            self.reply(dt.datetime.now().strftime('Saat %H:%M'))
        elif action == 'date':
            self.reply(dt.datetime.now().strftime('%d.%m.%Y'))
        elif action == 'status':
            import psutil
            mem = psutil.virtual_memory()
            disk = psutil.disk_usage(os.environ.get('SystemDrive', 'C:') + '\\')
            self.reply(f'İşlemci yüzde {psutil.cpu_percent(interval=1):.0f}. '
                       f'Bellek yüzde {mem.percent:.0f}. Diskte {disk.free / 2**30:.0f} GB boş.')
        elif action in ('notepad', 'calculator', 'tasks'):
            program = {'notepad': 'notepad.exe', 'calculator': 'calc.exe', 'tasks': 'Taskmgr.exe'}[action]
            subprocess.Popen([str(Path(os.environ['WINDIR']) / 'System32' / program)])
            self.reply('Açıldı.')
        elif action == 'browser':
            os.startfile('https://www.google.com')
        elif action == 'report':
            result = subprocess.run(['powershell.exe', '-NoProfile', '-ExecutionPolicy', 'Bypass',
                                     '-File', str(ROOT / 'Performans-Raporu.ps1')], check=False)
            self.reply('Rapor kaydedildi.' if result.returncode == 0 else 'Rapor oluşturulamadı.')
        else:
            self.reply('Komutlar: ' + ', '.join(ACTIONS))
        return True

def listen(assistant, device=None):
    import sounddevice as sd
    from vosk import Model, KaldiRecognizer, SetLogLevel
    model_path = ROOT / 'models' / 'vosk-model-small-tr-0.3'
    if not model_path.is_dir():
        raise RuntimeError('Türkçe model eksik. Kurulum.ps1 dosyasını çalıştırın.')
    SetLogLevel(-1)
    model = Model(str(model_path))
    info = sd.query_devices(device, 'input')
    if any(name in normalize(info['name']) for name in ('stereo mix', 'stereo karisimi', 'what u hear')):
        raise RuntimeError('Mikrofon yerine Stereo Karışımı seçili. Windows Ses ayarlarında gerçek mikrofonu varsayılan giriş yapın veya --device ile seçin.')
    rate = int(info['default_samplerate'])
    recognizer = KaldiRecognizer(model, rate)
    chunks = queue.Queue(maxsize=32)
    def callback(data, frames, time, status):
        if status:
            print('Mikrofon:', status, file=sys.stderr)
        try:
            chunks.put_nowait(bytes(data))
        except queue.Full:
            pass
    assistant.reply('Hazırım. Jarvis saat kaç diyebilirsiniz. Çıkmak için Control C.')
    # Sesli yanit sirasinda mikrofon kapatilir; asistan kendini komut sanmaz.
    with sd.RawInputStream(samplerate=rate, blocksize=4000, device=device,
                           dtype='int16', channels=1, callback=callback) as stream:
        while True:
            if not recognizer.AcceptWaveform(chunks.get()):
                continue
            text = json.loads(recognizer.Result()).get('text', '')
            if text:
                print('Duyulan:', text, flush=True)
            action = resolve(text, voice=True)
            if action:
                stream.stop()
                try:
                    if not assistant.execute(action):
                        return
                finally:
                    while not chunks.empty():
                        chunks.get_nowait()
                    recognizer.Reset()
                stream.start()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--text', action='store_true', help='Mikrofonsuz yazili komut')
    parser.add_argument('--devices', action='store_true')
    parser.add_argument('--device', type=int)
    parser.add_argument('--silent', action='store_true')
    args = parser.parse_args()
    if args.devices:
        import sounddevice as sd
        print(sd.query_devices())
        return
    assistant = Assistant(not args.silent)
    if args.text:
        print('Jarvis yazili mod. Yardim icin yardim yazin.')
        while True:
            action = resolve(input('> '))
            if not assistant.execute(action):
                break
    else:
        listen(assistant, args.device)

if __name__ == '__main__':
    try:
        main()
    except (KeyboardInterrupt, EOFError):
        print('\nJarvis kapandi.')
    except Exception as exc:
        print(f'Başlatılamadı: {exc}', file=sys.stderr)
        sys.exit(1)
