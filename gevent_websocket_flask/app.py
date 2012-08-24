import os, json
from gevent import pywsgi
from geventwebsocket.handler import WebSocketHandler
from flask import Flask, request, render_template
from docutils.core import publish_doctree, publish_parts
from xml.sax.saxutils import escape, unescape

app = Flask(__name__)

settings = {
    'stylesheet': '',
    'stylesheet_path': None,
}

@app.route('/')
def index():
    if not request.environ.get('wsgi.websocket'):
        return render_template('index.html')

    ws = request.environ['wsgi.websocket']
    while True:
        src = ws.receive()
        if src is None:
            break
        parts = publish_parts(src, writer_name='html', settings_overrides=settings)
        doc = publish_doctree(src)

        xmldoc = unescape(doc.asdom().toprettyxml('    '), {'&quot;': '"'})

        ws.send(json.dumps({'html': parts['html_body'],
                            'doctree': escape(xmldoc),
                            'htmltag': escape(parts['html_body'])}))
    return

@app.route('/<page>', methods=['GET'])
def page(page = ''):
    return render_template('%s.html' % page)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    server = pywsgi.WSGIServer(('0.0.0.0', port), app, handler_class=WebSocketHandler)
    server.serve_forever()

