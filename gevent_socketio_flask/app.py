import os, json
from gevent import monkey
from socketio import socketio_manage
from socketio.server import SocketIOServer
from socketio.namespace import BaseNamespace
from socketio.mixins import RoomsMixin, BroadcastMixin
from flask import Flask, request, render_template
from docutils.core import publish_doctree, publish_parts
from xml.sax.saxutils import escape, unescape

monkey.patch_all()

app = Flask(__name__)

@app.route('/')
def index():
    if not request.environ['PATH_INFO'].startswith('/socket.io'):
        return render_template('index.html')

@app.route('/socket.io/<path:remaining>')
def socketio(remaining):
    socketio_manage(request.environ, {'': DocNamespace}, request)
    return Response()

@app.route('/<page>', methods=['GET'])
def page(page = ''):
    return render_template('%s.html' % page)


class DocNamespace(BaseNamespace, RoomsMixin, BroadcastMixin):
    settings = {
        'stylesheet': '',
        'stylesheet_path': None,
    }

    def recv_message(self, message):
        parts = publish_parts(message, writer_name='html', settings_overrides=self.settings)
        doc = publish_doctree(message)
        xmldoc = unescape(doc.asdom().toprettyxml('    '), {'&quot;': '"'})
        self.send(json.dumps({'html': parts['html_body'],
                              'doctree': escape(xmldoc),
                              'htmltag': escape(parts['html_body'])}))


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    SocketIOServer(('0.0.0.0', port), app, resource='socket.io').serve_forever()

