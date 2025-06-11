import os, sys

sys.path.append("/home/alfrededison.helioho.st/httpdocs/vn30")

sys.path.insert(0, os.path.dirname(__file__))
from flask_app import app as application

application.secret_key = '3urf04u03jfjHG^%R^%E'