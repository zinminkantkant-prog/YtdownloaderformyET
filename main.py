~/yt4wrb $ cat main.py
import threading
import time
from app import app
from kivy.app import App
from kivy.clock import Clock
from android.runnable import run_on_ui_thread
from jnius import autoclass

# Android Native WebView Call
WebView = autoclass('android.webkit.WebView')
WebViewClient = autoclass('android.webkit.WebViewClient')
activity = autoclass('org.kivy.android.PythonActivity').mActivity

def start_flask():
    # Flask ကို Background ထဲမှာ Localhost ဖြင့် run မည်
    app.run(host="127.0.0.1", port=5000, debug=False)

class YTDownloaderApp(App):
    def build(self):
        # 1. Flask server ကို Thread တစ်ခုဖြင့် စတင်မည်
        threading.Thread(target=start_flask, daemon=True).start()

        # 2. Server တက်လာရန် ၁ စက္ကန့် စောင့်ပြီး WebView ဖြင့် ဖွင့်မည်
        Clock.schedule_once(self.create_webview, 1)
        return

    @run_on_ui_thread
    def create_webview(self, *args):
        webview = WebView(activity)
        webview.getSettings().setJavaScriptEnabled(True)
        webview.getSettings().setDomStorageEnabled(True)
        webview.setWebViewClient(WebViewClient())
        activity.setContentView(webview)
        webview.loadUrl('http://127.0.0.1:5000')

if __name__ == '__main__':
    YTDownloaderApp().run()
