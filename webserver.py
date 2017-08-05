from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import cgi
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from database_setup import Restaurant, Base, MenuItem

#Create db session
engine = create_engine('sqlite:///restaurantmenu.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

class WebServerHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        if self.path.endswith("/hello"):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            message = ""
            message += "<html><body>Hello!"
            message += "<form method='POST' enctype='multipart/form-data' action='/hello'><h2>What would you like me " \
                      "to say?</h2><input name='message' type='text' ><input type='submit' value='Submit'></form>"
            message += "</body></html>"
            self.wfile.write(message)
            print(message)
            return

        if self.path.endswith("/hola"):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            message = ""
            message += "<html><body>&#161Hola!<p> <a href = '/hello'>Back to Hello</a>"
            message += "<form method='POST' enctype='multipart/form-data' action='/hello'><h2>What would you like me " \
                       "to say?</h2><input name='message' type='text' ><input type='submit' value='Submit'></form>"
            message += "</body></html>"
            self.wfile.write(message)
            print(message)
            return

        if self.path.endswith("/restaurants"):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            all_restaurants = session.query(Restaurant).all()
            message = ""
            message += "<html><body>"
            message += '<a href="/restaurants/new">Create new restaurant here</a><p>'
            for r in all_restaurants:
                message += str(r.name) + "<br>"
                message += '<a href="/restaurants/%s/edit">Edit</a><br>' % r.id
                message += '<a href="/restaurants/%s/delete">Delete</a><br>' % r.id
                message += '<p>'
            message += "</body></html>"
            self.wfile.write(message)
            print(message)
            return

        if self.path.endswith("/restaurants/new"):
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            message = ""
            message += "<html><body><h1>Make a New Restaurant</h1>"
            message += "<form method='POST' enctype='multipart/form-data' action='/restaurants/new'>" \
                       "<input name='message' type='text'><input type='submit' value='Create'></form>"
            message += "</body></html>"
            self.wfile.write(message)
            print(message)
            return

        if self.path.endswith("/edit"):
            r_id = self.path.split("/")[2]
            r = session.query(Restaurant).filter_by(id = r_id).one()

            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            message = ""
            message += "<html><body><h1>Rename restaurant: %s</h1>" % r.name
            message += "<form method='POST' enctype='multipart/form-data' action='/restaurants/%s/edit'>" % r_id
            message += "<input name='message' type='text'><input type='submit' value='Rename'></form>"
            message += "</body></html>"
            self.wfile.write(message)
            print(message)
            return

        if self.path.endswith("/delete"):
            r_id = self.path.split("/")[2]
            r = session.query(Restaurant).filter_by(id = r_id).one()

            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            message = ""
            message += "<html><body><h1>Really DELETE '%s'?</h1>" % r.name
            message += "<form method='POST' enctype='multipart/form-data' action='/restaurants/%s/delete'>" % r_id
            message += "<button type='submit' value='DELETE'>DELETE</button><br>"
            message += "<a href='/restaurants'>Cancel</a></form>"
            message += "</body></html>"
            self.wfile.write(message)
            print(message)
            return

        else:
            self.send_error(404, 'File Not Found: %s' % self.path)

    def do_POST(self):
        try:

            if self.path.endswith("/restaurants/new"):
                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('message')

                    #Restaurant object
                    new_r = Restaurant(name = messagecontent[0])
                    session.add(new_r)
                    session.commit()

                    #redirect after creation
                    self.send_response(301)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Location', '/restaurants')
                    self.end_headers()

            if self.path.endswith("/edit"):
                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('message')

                    #Restaurant object rename
                    r_id = self.path.split("/")[2]
                    r = session.query(Restaurant).filter_by(id=r_id).one()
                    r.name = messagecontent[0]
                    session.add(r)
                    session.commit()

                    #redirect after creation
                    self.send_response(301)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Location', '/restaurants')
                    self.end_headers()

            if self.path.endswith("/delete"):
                ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
                if ctype == 'multipart/form-data':
                    fields = cgi.parse_multipart(self.rfile, pdict)
                    messagecontent = fields.get('message')

                    #Restaurant object rename
                    r_id = self.path.split("/")[2]
                    r = session.query(Restaurant).filter_by(id=r_id).one()
                    session.delete(r)
                    session.commit()

                    #redirect after creation
                    self.send_response(301)
                    self.send_header('Content-type', 'text/html')
                    self.send_header('Location', '/restaurants')
                    self.end_headers()

            if self.path.endswith("/hello"):
                self.send_response(301)
                self.end_headers()
                output = ""
                output += "<html><body>"
                output += " <h2> Okay, how about this: </h2>"
                output += "<h1> %s </h1>" % messagecontent[0]

                output += "<form method='POST' enctype='multipart/form-data' action='/hello'><h2>What would you like me " \
                          "to say?</h2><input name='message' type='text' ><input type='submit' value='Submit'></form>"
                output += "</body></html>"
                self.wfile.write(output)
                print(output)

        except:
            pass



def main():
    try:
        port = 8080
        server = HTTPServer(('', port), WebServerHandler)
        print "Web Server running on port %s" % port
        server.serve_forever()
    except KeyboardInterrupt:
        print " ^C entered, stopping web server...."
        server.socket.close()

if __name__ == '__main__':
    main()