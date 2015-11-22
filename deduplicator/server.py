from http.server import BaseHTTPRequestHandler


class DupServer(BaseHTTPRequestHandler):
    'Basic http request handler'

    is_dup = None

    def do_GET(self):
        '''Returns json response {"duplicates":true} or false
        expects user ids as two last components of url.
        e.g. http://localhost/1234/4321'''
        try:
            parts = self.path.strip("/").split("/")
            user1_id = parts[-2]
            user2_id = parts[-1]
            duplicates = self.is_dup(user1_id, user2_id)
            body = '{{"duplicates": {}}}'.format(duplicates).lower()
        except:
            self.send_response(400)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.wfile.write(bytes('Bad parameters', 'utf-8'))
            return

        self.send_response(200)
        self.send_header("Content-type", "text/json")
        self.end_headers()
        self.wfile.write(bytes(body, 'utf-8'))
