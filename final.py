from http.server import HTTPServer, BaseHTTPRequestHandler
from pymongo import MongoClient
import json
from urllib.parse import parse_qs
from gtts import gTTS
import os
import miniaudio
import re

# open json file and give it to data variable as a dictionary
with open("db.json") as data_file:
    data = json.load(data_file)

try:
    connect = MongoClient()
    print("Connected successfully!!!")
except:
    print("Could not connect to MongoDB")

# connecting or switching to the database
db = connect.demoAPIDB

# creating or switching to demoCollection
collection = db.apiCollection


# Defining a HTTP request Handler class
class ServiceHandler(BaseHTTPRequestHandler):
    # sets basic headers for the server
    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/json')
        # reads the length of the Headers
        length = int(self.headers['Content-Length'])
        # reads the contents of the request
        content = self.rfile.read(length)
        input = str(content).strip('b\'')
        self.end_headers()
        return input

    ######
    # LIST#
    ######
    # GET Method Definition
    def do_GET(self):

        # defining all the headers
        # Extract values from the query string
        try:
            # TO DO - get a requested therapy from database and send transcript along with audio to caller
            if None != re.search('/api/getTherapy/*', self.path):
                path, _, query_string = self.path.partition('?')
                queryparams = parse_qs(query_string)
                print(u"[START]: Received GET for %s with query: %s" % (path, queryparams))

                # set success header
                self.setSuccessHeader()

                requestType = "requestType"

                # if query is not None and len(query) > 0 and not query.__contains__("isAudioRequired"):
                if queryparams is not None and len(queryparams) > 0:
                    print(u"Requested Therapy: %s" % queryparams[requestType])
                    if queryparams[requestType] is not None:
                        key = queryparams[requestType]
                        text = data[key[0]]
                        print(u"Therapy fetched from database : %s" % text)
                        audiofromtext = self.convertSingleTextToSpeech(text)
                        os.system("start %s" % audiofromtext)
                        self.wfile.write(json.dumps(text).encode())

            # get users historical performance reports from database and send back to caller.
            elif None != re.search('/api/getUserPerformanceDetails/*', self.path):
                # TO DO - load data from actual database
                with open('samplejson/userPerformanceReport.json') as f:
                    data = json.load(f)

                if None != data:
                    print(data)
                    # set success header
                    self.setSuccessHeader()
                    self.wfile.write(json.dumps(data).encode())

                else:
                    self.setFailureHeader()

            # TO DO - get users historical performance reports from database and send back to caller.
            elif None != re.search('/api/getCustomizedTherapy/*', self.path):
                # load data from actual database
                with open('samplejson/customizedTherapy.json') as f:
                    data = json.load(f)

                if None != data:
                    print(data)
                    # set success header
                    self.setSuccessHeader()
                    self.wfile.write(json.dumps(data).encode())

                else:
                    self.setFailureHeader()

            else:
                # prints all the keys and values of the json file
                self.wfile.write(json.dumps(data).encode())
                self.convertTextToSpeech()
                # self.playAudioInBackground()

        except Exception as e:
            print("Exception occurred while processing request : %s" % e)
            self.setFailureHeader()

    def setFailureHeader(self):
        error = "DATA NOT FOUND!"
        self.wfile.write(bytes(error, 'utf-8'))
        self.send_response(404)

    def setSuccessHeader(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/json')
        self.end_headers()

    def playAudioInBackground(self):
        stream = miniaudio.stream_file("output.wav")
        with miniaudio.PlaybackDevice() as device:
            device.start(stream)
            input("Audio file playing in the background. Enter to stop playback: ")

    def convertTextToSpeech(self):
        myText = data["Theraphy1"]
        language = 'en'
        output = gTTS(text=myText, lang=language, slow=False)
        output.save("output.wav")
        os.system("start output.wav")

    def convertSingleTextToSpeech(self, myText):
        language = 'en'
        output = gTTS(text=myText, lang=language, slow=False)
        output.save("therapy.wav")
        return output

    def do_getTheraphy(self):
        display = {}
        input = self._set_headers()
        print("value of input", input)

        try:
            text_from_db = collection.find_one({}, {'_id': 0, input: 1})
            print("Text from database: ", text_from_db[input])
            text_from_db = text_from_db[input]

            # check if the key is present in the dictionary
            display[input] = text_from_db
            # print the keys required from the json file
            self.wfile.write(json.dumps(display).encode())
        except:
            self.setFailureHeader()

    ########
    # UPDATE#
    ########
    # PUT method Defination
    def do_PUT(self):
        collection.insert_one(data)
        self.send_response(200)


# Server Initialization
server = HTTPServer(('127.0.0.1', 8090), ServiceHandler)
server.serve_forever()
