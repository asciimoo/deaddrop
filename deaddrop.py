#!/usr/bin/env python2.6

import cgi
import os
import gnupg
from tempfile import mkdtemp
from StringIO import StringIO
from BaseHTTPServer import BaseHTTPRequestHandler
from BaseHTTPServer import HTTPServer

html = """
<form enctype="multipart/form-data" method="post">File: <input type="file" name="file"><input type="submit" value="Upload"></form>
"""
gpg = None
basePath = os.path.abspath(os.path.dirname(__file__))
gpgFingerprint = ''

class RequestHandler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        global html
        self.send_response(200)
        self.end_headers()
        self.wfile.write(html)
        return

    def do_POST(self):
        global gpg, basePath
        try:
            ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
            if ctype == 'multipart/form-data':
                query=cgi.parse_multipart(self.rfile, pdict)
        except:
            return
        self.send_response(301)
        self.end_headers()
        dropDir = mkdtemp(dir=basePath+'/drop/')
        gpg.encrypt_file(StringIO(query.get('file')), gpgFingerprint, output=dropDir + '/file', always_trust=True)
        self.wfile.write("POST OK.");
        return

if __name__ == '__main__':
    gpg = gnupg.GPG(gnupghome=basePath +'/gnupg/')
    server = HTTPServer(('localhost', 1234), RequestHandler)
    print '[!] Starting server, use <Ctrl-C> to stop'
    server.serve_forever()
