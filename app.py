"""harunokmen | JARVIS: local desktop assistant."""
import datetime
import json
import math
import os
from pathlib import Path
import queue
import threading
import time
import tkinter as tk
from tkinter import ttk, messagebox
import core

BG, PANEL, FG, CYAN = '#071018', '#101f2b', '#d9edf5', '#42dfdf'
EFFECTS = {'notepad', 'calculator', 'tasks', 'browser', 'report'}

class App:
    def __init__(self, root):
        self.root = root
        self.events = queue.Queue()
        self.cancel = threading.Event()
        self.busy = False
        self.phase = 0
        root.title('JARVIS • harunokmen')
        root.geometry('1050x740')
        root.minsize(860, 680)
        root.configure(bg=BG)
        root.protocol('WM_DELETE_WINDOW', self.close)
        top = tk.Frame(root, bg=BG)
        top.pack(fill='x', padx=24, pady=18)
        tk.Label(top, text='J A R V I S', font=('Segoe UI', 26, 'bold'), fg=CYAN, bg=BG).pack(side='left')
        tk.Label(top, text='harunokmen  /  KİŞİSEL ASİSTAN', fg=FG, bg=BG).pack(side='right')
        body = tk.Frame(root, bg=BG)
        body.pack(fill='both', expand=True, padx=24)
        left = tk.Frame(body, bg=PANEL, width=290)
        left.pack(side='left', fill='y', padx=(0, 16))
        left.pack_propagate(False)
        self.canvas = tk.Canvas(left, width=280, height=240, bg=PANEL, highlightthickness=0)
        self.canvas.pack(pady=10)
        self.state = tk.StringVar(value='HAZIR • MİKROFON KAPALI')
        tk.Label(left, textvariable=self.state, bg=PANEL, fg=CYAN, wraplength=265).pack(pady=8)
        self.metrics = tk.StringVar(value='Sistem durumu yükleniyor…')
        tk.Label(left, textvariable=self.metrics, bg=PANEL, fg=FG, justify='left', font=('Segoe UI', 11)).pack(pady=12)
        self.button(left, 'Sistem durumu', lambda: self.submit('sistem durumu')).pack(fill='x', padx=16, pady=4)
        self.button(left, 'Performans raporu', lambda: self.submit('performans raporu')).pack(fill='x', padx=16, pady=4)
        self.button(left, 'Komut listesi', lambda: self.submit('yardım')).pack(fill='x', padx=16, pady=4)
        tk.Label(left, text='YEREL SES İŞLEME\nİŞLEM ÖNCESİ ONAY\nİZİN LİSTELİ KOMUTLAR', bg=PANEL, fg='#8bafba', justify='left').pack(pady=20)
        right = tk.Frame(body, bg=BG)
        right.pack(side='left', fill='both', expand=True)
        self.history = tk.Text(right, bg=PANEL, fg=FG, font=('Segoe UI', 11), wrap='word', relief='flat', padx=16, pady=16, state='disabled')
        self.history.pack(fill='both', expand=True)
        self.entry = tk.Entry(right, bg=PANEL, fg=FG, insertbackground=CYAN, font=('Segoe UI', 12), relief='flat')
        self.entry.pack(fill='x', pady=(12, 8), ipady=12)
        self.entry.bind('<Return>', lambda event: self.submit())
        self.button(right, 'Komutu gönder', self.submit).pack(fill='x')
        audio = tk.Frame(root, bg=BG)
        audio.pack(fill='x', padx=24, pady=12)
        self.devices = ttk.Combobox(audio, state='readonly', width=42)
        self.devices.pack(side='left')
        self.device_ids = []
        self.button(audio, 'Yenile', self.refresh_devices).pack(side='left', padx=6)
        self.mic = self.button(audio, 'Konuş (en fazla 8 sn)', self.record)
        self.mic.pack(side='left', padx=6)
        self.button(audio, 'Durdur', self.cancel.set).pack(side='left')
        self.speak = tk.BooleanVar(value=False)
        tk.Checkbutton(root, text='Yanıtları seslendir (Windows sesi)', variable=self.speak, bg=BG, fg=FG, selectcolor=PANEL, activebackground=BG).pack()
        tk.Label(root, text='© 2026 harunokmen • v0.2 • Ses ve sohbet geçmişi diske kaydedilmez', bg=BG, fg='#8bafba').pack(pady=10)
        self.log('Jarvis', 'Hoş geldin Harun. “saat kaç” yazabilir veya mikrofon seçerek konuşabilirsin. Uygulama açma ve rapor oluşturma işlemleri için onay isterim. Serbest sohbet modeli henüz bağlı değil.')
        self.refresh_devices()
        self.tick()
        self.poll()
        self.telemetry()

    def button(self, parent, text, command):
        return tk.Button(parent, text=text, command=command, bg='#163747', fg=FG, activebackground='#22556a', activeforeground='white', relief='flat', padx=10, pady=9)

    def log(self, who, text):
        self.history.configure(state='normal')
        self.history.insert('end', f'{who}  ·  {datetime.datetime.now():%H:%M}\n{text}\n\n')
        self.history.configure(state='disabled')
        self.history.see('end')

    def refresh_devices(self):
        try:
            import sounddevice as sd
            inputs = [(i, d['name']) for i, d in enumerate(sd.query_devices()) if d['max_input_channels'] > 0 and not any(x in core.normalize(d['name']) for x in ('stereo mix', 'stereo karisimi', 'what u hear', 'mapper', 'eslestiricisi', 'birincil', 'primary sound'))]
            self.device_ids = [i for i, _ in inputs]
            self.devices['values'] = [f'{i}: {name}' for i, name in inputs]
            if inputs:
                self.devices.current(0)
            else:
                self.devices.set('Gerçek mikrofon bulunamadı')
        except Exception as exc:
            self.log('Ses aygıtı', str(exc))

    def submit(self, text=None):
        if self.busy:
            return
        text = text if text is not None else self.entry.get().strip()
        if not text:
            return
        self.entry.delete(0, 'end')
        self.log('Harun', text)
        action = core.resolve(text) or core.resolve(text, voice=True)
        if action is None:
            self.log('Jarvis', 'Bu komut izin listemde yok. “yardım” yazarak desteklenen komutları görebilirsin.')
            return
        if action == 'exit':
            self.cancel.set()
            self.log('Jarvis', 'Dinleme kapalı.')
            return
        if action in EFFECTS and not messagebox.askyesno('İşlem onayı', f'Şu komut çalıştırılsın mı?\n\n{text}', parent=self.root):
            self.log('Jarvis', 'İşlem iptal edildi.')
            return
        self.busy = True
        self.state.set('İŞLENİYOR')
        speech = self.speak.get()
        def work():
            try:
                assistant = core.Assistant(speak=speech)
                original = assistant.reply
                def reply(message):
                    self.events.put(('reply', message))
                    original(message)
                assistant.reply = reply
                assistant.execute(action, approved=True)
            except Exception as exc:
                self.events.put(('reply', f'İşlem tamamlanamadı: {exc}'))
            finally:
                self.events.put(('done', None))
        threading.Thread(target=work, daemon=True).start()

    def record(self):
        if self.busy:
            return
        index = self.devices.current()
        if index < 0 or index >= len(self.device_ids):
            messagebox.showinfo('Mikrofon', 'Mikrofon bağlayıp Yenile düğmesine basın.')
            return
        device = self.device_ids[index]
        self.cancel.clear()
        self.busy = True
        self.state.set('MODEL HAZIRLANIYOR')
        def capture():
            try:
                import sounddevice as sd
                from vosk import Model, KaldiRecognizer, SetLogLevel
                info = sd.query_devices(device, 'input')
                if any(x in core.normalize(info['name']) for x in ('stereo mix', 'stereo karisimi', 'what u hear')):
                    raise RuntimeError('Stereo Karışımı yerine gerçek mikrofon seçin.')
                path = core.ROOT / 'models' / 'vosk-model-small-tr-0.3'
                if not path.is_dir():
                    raise RuntimeError('Model bulunamadı. Kurulum.ps1 dosyasını çalıştırın.')
                SetLogLevel(-1)
                if not hasattr(self, 'model'):
                    self.model = Model(str(path))
                rate = int(info['default_samplerate'])
                rec = KaldiRecognizer(self.model, rate)
                chunks = queue.Queue(maxsize=64)
                def callback(data, frames, timing, status):
                    try:
                        chunks.put_nowait(bytes(data))
                    except queue.Full:
                        pass
                if self.cancel.is_set():
                    return
                self.events.put(('state', 'DİNLİYOR • DURDUR İLE İPTAL'))
                result = ''
                with sd.RawInputStream(device=device, samplerate=rate, channels=1, dtype='int16', blocksize=4000, callback=callback):
                    until = time.monotonic() + 8
                    while time.monotonic() < until and not self.cancel.is_set():
                        try:
                            data = chunks.get(timeout=.15)
                        except queue.Empty:
                            continue
                        if rec.AcceptWaveform(data):
                            result = json.loads(rec.Result()).get('text', '')
                            if result:
                                break
                    if not result:
                        result = json.loads(rec.FinalResult()).get('text', '')
                if not self.cancel.is_set():
                    self.events.put(('heard', result))
            except Exception as exc:
                self.events.put(('reply', f'Ses girişi: {exc}'))
            finally:
                self.events.put(('capture_done', None))
        threading.Thread(target=capture, daemon=True).start()

    def poll(self):
        heard = None
        try:
            while True:
                kind, value = self.events.get_nowait()
                if kind == 'reply':
                    self.log('Jarvis', value)
                elif kind == 'state':
                    self.state.set(value)
                elif kind == 'heard':
                    heard = value
                elif kind in ('done', 'capture_done'):
                    self.busy = False
                    self.state.set('HAZIR • MİKROFON KAPALI')
        except queue.Empty:
            pass
        if heard is not None:
            # Recognition result and completion may arrive in separate UI ticks.
            self.pending_heard = heard
        if not self.busy and hasattr(self, 'pending_heard'):
            text = self.pending_heard
            del self.pending_heard
            if text:
                self.submit(text)
            else:
                self.log('Jarvis', 'Konuşma algılanmadı.')
        self.root.after(80, self.poll)

    def telemetry(self):
        try:
            import psutil
            mem = psutil.virtual_memory()
            disk = psutil.disk_usage(os.environ.get('SystemDrive', 'C:') + '\\')
            self.metrics.set(f'CPU   %{psutil.cpu_percent():.0f}\nRAM   %{mem.percent:.0f}\nBOŞ DİSK   {disk.free / 2**30:.0f} GB')
        except Exception:
            self.metrics.set('Sistem ölçümü kullanılamıyor')
        self.root.after(2000, self.telemetry)

    def tick(self):
        if self.root.state() != 'iconic':
            self.canvas.delete('all')
            self.phase += .035
            for r in (68, 86, 104):
                self.canvas.create_oval(140-r, 120-r, 140+r, 120+r, outline='#235363', width=1)
                self.canvas.create_arc(140-r, 120-r, 140+r, 120+r, start=(self.phase*40+r)%360, extent=75, style='arc', outline=CYAN, width=3)
            size = 45 + math.sin(self.phase*2)*3
            self.canvas.create_oval(140-size, 120-size, 140+size, 120+size, fill='#123747', outline=CYAN, width=2)
            self.canvas.create_text(140, 120, text='H', fill=FG, font=('Segoe UI', 32, 'bold'))
        self.root.after(65, self.tick)

    def close(self):
        self.cancel.set()
        self.root.destroy()

if __name__ == '__main__':
    root = tk.Tk()
    app = App(root)
    root.mainloop()
