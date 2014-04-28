import protobufwebui
import test_pb2
from BaseHTTPServer import HTTPServer

class MyHandler(protobufwebui.ProtobufUIHandler):
    def printPageSubmitted(self, request):
        protobufwebui.ProtobufUIHandler.printPageSubmitted(self, request)
        print req



def main():
    try:

        MyHandler.setRequestType(test_pb2.MyRequest)

        server = HTTPServer(('', 8055), MyHandler)
        server.serve_forever()
    except KeyboardInterrupt:
        print 'closing...'
        server.socket.close()


if __name__ == '__main__':
    main()
