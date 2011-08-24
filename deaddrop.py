#!/usr/bin/env python2.6

import cgi
import os
import gnupg
from tempfile import mkdtemp
from StringIO import StringIO
from BaseHTTPServer import BaseHTTPRequestHandler
from BaseHTTPServer import HTTPServer
from SocketServer import ThreadingMixIn

html = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml" lang="en" xml:lang="en">
<head><meta http-equiv="content-type" content="text/html; charset=utf-8" /><title>[!] DeadDrop</title></head>
<body><div>%s</div></body>
</html>
"""
gpg = None
basePath = os.path.abspath(os.path.dirname(__file__))
dropPath  = basePath + '/drop/'
gpgPath = basePath + '/gnupg/'
gpgFingerprint = '80C412B8'

class RequestHandler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        global html
        self.send_response(200)
        self.end_headers()
        if self.path.startswith('/drop/') and os.path.isdir(dropPath+self.path[6:]): return self.wfile.write(open(dropPath+self.path[6:]+'/file').read())
        if self.path == '/files': return self.wfile.write(html % ('<ul><li>'+'</li><li>'.join(['<a href="/drop/%s">%s</a>' % (x, x) for x in os.listdir(dropPath+'/') if x.startswith('tmp')] or ['no files'])+'</li></ul>'))
        return self.wfile.write(html % '<form enctype="multipart/form-data" method="post" action="/"><p>File: <input type="file" name="file" /><input type="submit" value="Upload" /></p></form>')

    def do_POST(self):
        global gpg, basePath, gpgFingerprint
        try:
            ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
            if ctype == 'multipart/form-data':
                query=cgi.parse_multipart(self.rfile, pdict)
        except:
            return
        self.send_response(301)
        self.end_headers()
        dropDir = mkdtemp(dir=dropPath)
        gpg.encrypt_file(StringIO(query.get('file')), gpgFingerprint, output=dropDir + '/file', always_trust=True)
        self.wfile.write("POST OK.");
        return

class ThreadingServer(ThreadingMixIn, HTTPServer):
    pass

if __name__ == '__main__':
    gpg = gnupg.GPG(gnupghome=gpgPath)
    server = ThreadingServer(('localhost', 1234), RequestHandler)
    print '[!] Starting server, use <Ctrl-C> to stop'
    server.serve_forever()
