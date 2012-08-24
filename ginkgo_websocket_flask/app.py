import os
from ginkgo import Service
from ginkgo.async.gevent import WSGIServer
from geventwebsocket.handler import WebSocketHandler
from flask import Flask, render_template
from docutils.core import publish_parts, publish_doctree
from xml.sax.saxutils import escape, unescape
import json

class WebSocket(Service):
    settings = {
        'stylesheet': '',
        'stylesheet_path': None,
    }

    def __init__(self):
        self.add_service(WSGIServer(('0.0.0.0', 5001), self.handle, handler_class=WebSocketHandler))

    def handle(self, environ, start_response):
        if environ.get('wsgi.websocket'):
            ws = environ['wsgi.websocket']
            while True:
                src = ws.receive()
                if src is None:
                    break
                parts = publish_parts(src, writer_name='html', settings_overrides=self.settings)
                doc = publish_doctree(src)

                xmldoc = unescape(doc.asdom().toprettyxml('    '), {'&quot;': '"'})

                ws.send(json.dumps({'html': parts['html_body'],
                                    'doctree': escape(xmldoc),
                                    'htmltag': escape(parts['html_body'])}))


class Http(Service):
    app = Flask(__name__)

    def __init__(self):
        port = int(os.environ.get('PORT', 5000))
        self.add_service(WSGIServer(('0.0.0.0', port), self.app))

    @app.route('/', methods=['GET'])
    def index():
        return render_template('index.html')

    @app.route('/<page>', methods=['GET'])
    def page(page = ''):
        return render_template('%s.html' % page)


class Application(Service):
    def __init__(self):
        self.add_service(Http())
        self.add_service(WebSocket())

