from http.server import BaseHTTPRequestHandler, HTTPServer
from io import BytesIO
import json
import os
import ssl


def check_validity(k8s_object_dict):
	return False


class WebhookAdmissionServer(BaseHTTPRequestHandler):
	def _set_response(self, status, bytes_ = None):
		self.send_response(status)
		self.send_header('Content-type', 'application/json')
		self.end_headers()
		if bytes_:
			self.wfile.write(bytes_)

	def do_POST(self):

		try:
			length = int(self.headers['content-length'])
			data = self.rfile.read(length)
			k_json = json.loads(str(data,'utf8')) 
		except (TypeError, json.decoder.JSONDecodeError):
			return self._set_response(500)

		print(k_json)

		verdict = check_validity(k_json)

		try:
			body = {
				"kind": "AdmissionReview",
				"apiVersion": "admission.k8s.io/v1beta1",
				"request": k_json['request'],
				"response" : {}
				}
		except KeyError:
			self._set_response(500)

		response = BytesIO()
		response.write(bytes(json.dumps(body, indent = 2), 'utf8'))
		self._set_response(200, response.getvalue())

TLS = os.environ.get('TLS', False)
if TLS:
	try:
		KEY = os.environ['KEY_PATH']
		CERT = os.environ['CERT_PATH']
		os.stat(KEY)
		os.stat(CERT)
		DEBUG = False
	except KeyError:
		os.system("openssl req -x509 -newkey rsa:1024 -keyout key.pem -out cert.pem -days 365")
		KEY = 'key.pem'
		CERT = 'cert.pem'
		DEBUG = True

if __name__ == '__main__':
	
	webhook = HTTPServer(('', 8443), WebhookAdmissionServer)
	# Taken from:
	#	https://blog.anvileight.com/posts/simple-python-http-server/
	if TLS:
		webhook.socket = ssl.wrap_socket (webhook.socket, 
				keyfile=KEY, 
				certfile=CERT, server_side=True)

	try:
		webhook.serve_forever()
	except KeyboardInterrupt:
		if TLS and DEBUG:
			os.unlink(KEY)
			os.unlink(CERT)

