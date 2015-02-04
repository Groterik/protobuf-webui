import string, cgi
from BaseHTTPServer import BaseHTTPRequestHandler
import google.protobuf
from google.protobuf.descriptor import FieldDescriptor as FD
import base64
import urlparse

def setAttrByPath(obj, path, value):
    att = getattr(obj, path[0])
    if len(path) > 1:
        setAttrByPath(att, path[1:], value)
    else:
        setattr(obj, path[0], value)

def getFDRecursive(d, path):
    fd = d.fields_by_name[path[0]]
    if len(path) > 1:
        return getFDRecursive(fd.message_type, path[1:])
    else:
        return fd

def getFDByPath(obj, path):
    return getFDRecursive(obj.DESCRIPTOR, path)

class ProtobufUIHandler(BaseHTTPRequestHandler):
    __depth = 0
    __requestType = type(int)

    @staticmethod
    def getRequestType():
        return ProtobufUIHandler.__requestType

    @staticmethod
    def setRequestType(t):
        ProtobufUIHandler.__requestType = t



    def printHeader(self):
        self.wfile.write('<p><h1>' + ProtobufUIHandler.getRequestType().DESCRIPTOR.full_name + '</h1></p>')

    def do_GET(self):
        try:
            self.send_response(200)
            self.send_header('Content-type',	'text/html')
            self.end_headers()
            qs = {}
            path = self.path
            if '?' in path:
                path, tmp = path.split('?', 1)
                qs = urlparse.parse_qs(tmp)
                print path, qs
                self.parseGET(qs)
                return

            self.wfile.write('<html><body>')

            self.wfile.write('<form action=\"' + path + '\" enctype=\"multipart/form-data\" method=\"get\">')

            self.printHeader()

            self.printMessage(ProtobufUIHandler.getRequestType().DESCRIPTOR, ProtobufUIHandler.getRequestType().DESCRIPTOR.name, 0)

            self.wfile.write('<input type=\"submit\" name=\"submit_button\" /> ')
            self.wfile.write('</form>')

            self.wfile.write('</body></html>')

            return

        except IOError:
            self.send_error(404,'File Not Found: %s' % self.path)

    def paddingOpen(self):
        self.wfile.write('<p><span style=\"padding: 0 ' + str(self.__depth * 20) + 'px\">')
    def paddingClose(self):
        self.wfile.write('</span></p>')

    def printCheckbox(self, name, fd):
        self.wfile.write('<input type=\"checkbox\"')

        if fd.label == 2:
            self.wfile.write(' onchange=\"this.checked=true;\"')
            self.wfile.write(' checked=\"\"checked\"')
        else:
            self.wfile.write(' onchange=\"if (!this.checked) {document.getElementById(\'' + name + '\').setAttribute(\'disabled\', \'disabled\');} else {document.getElementById(\'' + name + '\').removeAttribute(\'disabled\');}\"')

        self.wfile.write('/>');

    def printFieldName(self, name, fd):
        self.wfile.write(fd.name);

    def printEnum(self, name, fd):
        self.wfile.write('<select name=\"' + name + '\" required id=\"' + name + '\"')
        if not fd.label == 2:
            self.wfile.write('disabled')
        self.wfile.write('>')
        enum_t = fd.enum_type
        for v in enum_t.values:
            self.wfile.write('<option value=\"' + v.name + '\">' + v.name + ' = ' + str(v.number) + '</option>')
        self.wfile.write('</select>')

    def printInputbox(self, name, fd):
        self.wfile.write('<input type=\"text\" name=\"' + name + '\" id=\"' + name + '\" value=\"\"')
        if not fd.label == 2:
            self.wfile.write(' disabled=\"disabled\"')
        self.wfile.write('/>')


    def printField(self, desc, prefix):
        name = prefix + '.' + desc.name;
        is_required = (desc.label == 2)

        self.paddingOpen()
        self.printCheckbox(name, desc)
        self.printFieldName(name, desc)

        if desc.type == FD.TYPE_MESSAGE:
            self.printMessage(desc.message_type, name, not is_required)
        elif desc.type == FD.TYPE_ENUM:
            self.printEnum(name, desc)
        else:
            self.printInputbox(name, desc)


    def printMessage(self, desc, prefix, disabled):
        self.__depth += 1;

        self.wfile.write('<fieldset name=\"' + prefix + '\" id=\"' + prefix + '\"')
        if disabled:
            self.wfile.write(' disabled')

        self.wfile.write('>')

        for f in desc.fields:
            self.printField(f, prefix);

        self.wfile.write('</fieldset>')

        self.__depth -= 1;


    def printPageSubmitted(self, req):
        self.wfile.write('<h1>' + req.DESCRIPTOR.full_name + '</h1>')
        self.wfile.write('<pre>' + str(req) + '</pre>')
        self.wfile.write('<br></br><b>BASE64:</b><br></br>')
        self.wfile.write(base64.b64encode(req.SerializeToString()))

    def processRequest(self, req):
        self.send_response(200)
        self.send_header('Content-type',	'text/html')
        self.end_headers()
        self.wfile.write('<html><body>')

        self.printPageSubmitted(req)

        self.wfile.write('</body></html>')

    def parseGET(self, qs):
        try:

            req = ProtobufUIHandler.getRequestType()()

            for k, v in qs.iteritems():
                path = k.split('.')
                value = v[0]
                if len(path) > 0 and path[0] == ProtobufUIHandler.getRequestType().DESCRIPTOR.name:
                    path = path[1:]
                    fd = getFDByPath(req, path)
                    if fd.type == FD.TYPE_ENUM:
                        setAttrByPath(req, path, fd.enum_type.values_by_name[value].number)
                    elif fd.type == FD.TYPE_INT32 or fd.type == FD.TYPE_UINT32:
                        setAttrByPath(req, path, int(value))
                    elif fd.type == FD.TYPE_INT64 or fd.type == FD.TYPE_UINT64:
                        setAttrByPath(req, path, long(value))
                    else:
                        setAttrByPath(req, path, value)

            self.processRequest(req)
        except:
            raise
