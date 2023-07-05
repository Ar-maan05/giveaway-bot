import firebase_admin
from firebase_admin import db
import json

cred_obj = firebase_admin.credentials.Certificate('C:\\Users\\armaa\\Desktop\\vscode\\giveaway\\firebase.json')
default_app = firebase_admin.initialize_app(cred_obj, {
	'databaseURL':'https://discord-5ca97-default-rtdb.firebaseio.com'
	})

'''def create_giveaway_config(input: dict):
    ref = db.reference("/giveaway_config/")
    for i in input:
        '''

ref = db.reference('/giveaway_config/')
ref.set({"what":"up"})