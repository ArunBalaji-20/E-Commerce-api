from flask import Flask,jsonify
import uuid
from passlib.hash import pbkdf2_sha256
import re

class User:
    def signup(self,fname,lname,email_id,username,password):
        user={ "_id": uuid.uuid4().hex,"firstName":fname,"lastName":lname,"email_id":email_id,"username":username,"password":password}
        user['password']=pbkdf2_sha256.hash(user['password'])

        return user

    def sanitize(self,email):
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern,email) is not None
