import threading
import webview
import time
from app import app


def run_flask():
    app.run(host="127.0.0.1", port=5000, debug=False, use_reloader=False)


if __name__ == "__main__":

    # 🚀 Flask start
    t = threading.Thread(target=run_flask)
    t.daemon = True
    t.start()

    # 🪟 Splash screen HTML
    splash_html = """
<html>
<head>
<style>
.loader {
  border: 6px solid #f3f3f3;
  border-top: 6px solid #3498db;
  border-radius: 50%;
  width: 50px;
  height: 50px;
  animation: spin 1s linear infinite;
  margin:auto;
}
@keyframes spin {
  100% { transform: rotate(360deg); }
}
</style>
</head>
<body style="display:flex;justify-content:center;align-items:center;height:100vh;background:#111;color:white;">
<div style="text-align:center;">
<h2>Student Management</h2>
<div class="loader"></div>
<p>Loading...</p>
</div>
</body>
</html>
"""

    splash = webview.create_window("Student Management System", html=splash_html, width=500, height=300)

    def load_main():
        time.sleep(2)
        splash.load_url("http://127.0.0.1:5000")

    webview.start(load_main)