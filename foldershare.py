#!/usr/bin/env python3
import os
import sys
import argparse
import traceback
from subprocess import Popen, PIPE
from http.server import HTTPServer, BaseHTTPRequestHandler


# using 1 MB chunks when sending tar.gz stream
CHUNKSIZE = 1*1024*1024


class ShareHandler(BaseHTTPRequestHandler):
    '''
    Shared folder content HTTP handler
    '''

    def do_GET(self):
        '''
        HTTP GET method handler
        '''

        # default HTTP response attributes
        streaming = False
        code = 200
        headers = [('Connection', 'close')]
        body = None

        try:
            # processing request
            if self.path == '/':
                # show brief help page
                host = self.server.server_address[0]
                if host == '0.0.0.0':
                    host = 'localhost'
                port = self.server.server_address[1]
                headers.append(('Content-Type', 'text/html; charset=utf-8'))
                body = '''
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8" />
    <title>Shared Folder</title>
</head>
<body>
    <h3>
        Shared folder content is available as
        <a href="/files.tar.gz">/files.tar.gz</a> file
    </h3>
    <p>Command line download &amp; extract example:</p>
    <pre>
    curl http://{host}:{port}/files.tar.gz | tar xz</pre>
    <p>or:</p>
    <pre>
    wget http://{host}:{port}/files.tar.gz -O - | tar xz</pre>
    <p>
        Source code:
        <a href="https://github.com/xHasKx/foldershare" target="_blank">
            github.com/xHasKx/foldershare
        </href>
    </p>
</body>
</html>
                '''.strip().format(host=host, port=port).encode('utf-8')
            elif self.path == "/files.tar.gz":
                # send files as tar.gz archive
                with Popen('tar cz *', stdout=PIPE, shell=True) as p:
                    # subprocess started, start sending HTTP response
                    self.send_response(200)
                    for hdr in headers:
                        self.send_header(hdr[0], hdr[1])
                    self.send_header('Content-Type', 'application/tar+gzip')
                    self.end_headers()
                    # start streaming mode to prevent actions in finally block
                    streaming = True
                    while True:
                        # read each stdout chunk
                        chunk = p.stdout.read(CHUNKSIZE)
                        if not chunk:
                            # end of file reached
                            break
                        # and write each chunk to http response
                        self.wfile.write(chunk)
            else:
                # all other requests
                code = 404
        except:
            # handle any error - send HTTP 500 code
            code = 500
            headers.append(('Content-Type', 'text/plain'))
            body = b'Internal Server Error'
            # and show traceback on stdout
            traceback.print_exc()
        finally:
            if not streaming:
                # send generated HTTP answer if streaming mode is not started
                self.send_response(code)
                for hdr in headers:
                    self.send_header(hdr[0], hdr[1])
                self.end_headers()
                if body:
                    self.wfile.write(body)


def http_server(address, port):
    '''
    Start HTTP server on specified host and port
    '''

    # create HTTP server
    server = HTTPServer((address, port), ShareHandler)
    print('Starting HTTP server on {}:{} to share folder {}'.format(
          address, port, os.getcwd()))
    print('Press Ctrl+C (possible several times) to stop it')

    # and start its loop
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print()
    finally:
        print('Stopped HTTP server')


def main():
    '''
    Entry Point
    '''

    # parse args
    parser = argparse.ArgumentParser(
        description='Share folder content over HTTP server as tar.gz file')
    parser.add_argument('port', metavar='port', type=int,
                        default=8080, nargs='?',
                        help='Port to start HTTP server, default is 8080')
    parser.add_argument('address', metavar='address', type=str,
                        default="", nargs='?',
                        help='Network address to start HTTP server, ' +
                        'default is all interfaces')
    args = parser.parse_args()

    # check args are valid
    if args.port <= 0 or args.port > 65535:
        raise Exception("Invalid port: not in valid range: " + str(args.port))

    # start http server to share current folder
    http_server(args.address, args.port)


if __name__ == '__main__':
    main()
