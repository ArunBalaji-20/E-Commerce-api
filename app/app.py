from flask import Flask,render_template_string,request,make_response,jsonify
from pymongo import MongoClient
from passlib.hash import pbkdf2_sha256
from cryptography.hazmat.primitives import serialization
from users.models import User
import jwt
from bson import json_util, ObjectId
import json
import os
import requests
import uuid
app=Flask(__name__)

#Database connection
client=MongoClient(host='localhost',port=27017)
loginDb=client['auth']
loginCollection=loginDb['users']
db=client['products']
collection=db['items']
cartCollection=db['cart']
orderCollection=db['orders']
orderHistory=db['history']

#jwt token
#jwt=JWT()
private_key=b'''-----BEGIN PRIVATE KEY-----
MIIEuwIBADANBgkqhkiG9w0BAQEFAASCBKUwggShAgEAAoIBAQCyR5Bav0usLMq1
gkPnyefafNtAnTK5REExIiNUE5BvebgTfYQS3JKKiy2E97bF5IjIftTDHjjcu7tX
zfZ8oPilQhQxek7USQ9LstiOX9v6HkGNcjcdGaYk5HXxwDuzayS3Xly4GXEP4XXO
on3rmMNTxfv4ARo6FZ6+s4U1ylamnqbrUmxsWcTiCS3+xdIVx/fMNuZbck69rLvo
BvP5Gux2yS4ACxGjbeg9CgyhEI7voxt1z3Lk79gsC0T7w1/xCrx55dC1+qphj9Pr
FTiVpJmXINKfUo+OLmgeeZrTcrDrig9a2P6QuuCiRU9CqW7Rv9QS0sIGUpT1LkFw
s58nCfYlAgMBAAECgf81FzsgwOZYVlBc4RtWEdx3UHgtzXYWE+PUayjsFNZchR3Q
gEYseefsdzJcK8TgGnIBBajaCHwv46BDysfjYVegUyfDFfbqimamrb7syVylU5Wd
cQWGUH82k4dqBWBKjSBEImXv9bgbTNNF1yaIKq8l9c0jq7+8ctQ45thwK4IUzyeY
0ET3mvh3X4l1rhlYywJSNrAL5TLQQhA2v+eBhlKvryDBK+9g8lrjO/Zk0Tjx9FUk
MUbiUlmtJa5dnohPfKPjtOJAadS2u4EbPeMng9X7R9DjgGLV5wHEWvbBEYoIY+CI
I9/NWFFxX09q+jXcNgHhjsA+D0vY68nzVDJ8WGkCgYEA2zJXeP/3B7+9NTJNqZhW
HPSiHFTCcEpqcbqLBbcyN+qYKhwk97Mu8mqvNTe0yYeKGP0W7QrZ8EE8mHbwiFe8
9ZW/kG+tWXGIRK/eskbI3/6mugp9191tufRKqSuLyVbcRGhW6oHoti+AZdJD4wUE
SaMqXVB/zInArF3YHn+f9dkCgYEA0DZ+6KcoD2vBopzL1874J0+4WpvK/u/Z20H1
LoKZDtFRwJy+uYqbCMeW52QNwXsdQnGVup34u6Hbvq/ZWgMDxrlvjj3N+UJme/i9
DfXjC2scm30ZPNUXTrvG95nkJqZ0uBSIngpNMIWyB52GR+YMDPQOjAsGFfQeC3tA
uv/3Vy0CgYEAqodtufsZCnRHFR2/gdO8GubPP89JPecHDNed1KKDdTETlJ80u2gx
e/M3v+VIxwiljW9I6L1qdBmstMjDtK7dmQoZcJsRd+Z1p0pTrMqY+Hq65z3GTaw8
81B0zUvNgqQK1UV/aQ4MJ8Co2Y5Ntk5u2YMRMGuyIUSCGxcfTgroPXECgYA1X8Lo
oPEEAvuAU/FtQQEcErOPhqBi+dk++4l+grv5sG7kkUnTBlT3yzJD3sIn9wdpIPTh
Ad3hO3y5RRrSmDM/ngmazP0gCIV9AiZ0jbPGGY8bzNXLYlS3OiunDSwPPFxvU9Qx
rzJaXetlSFxD0hUEvQt9mtXUit+o0c+mIDengQKBgHx7pQL9q+GdiJiiariigZZO
5jc4+aYyMs4RH61tNQGoBoHlw0ayNWNd8f9zRRU7PepiAVpKDCzDvyHV3GwqKkg5
IOvNpefvG1aQF3m8PfM5b42/rJbTRpeZFPozQm75r28vMiIpI0w95sA5qNHBUaTs
+tqJtcdF3onsLLpvZwB+
-----END PRIVATE KEY-----'''

public_key=b'''-----BEGIN PUBLIC KEY-----
MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAskeQWr9LrCzKtYJD58nn
2nzbQJ0yuURBMSIjVBOQb3m4E32EEtySiosthPe2xeSIyH7Uwx443Lu7V832fKD4
pUIUMXpO1EkPS7LYjl/b+h5BjXI3HRmmJOR18cA7s2skt15cuBlxD+F1zqJ965jD
U8X7+AEaOhWevrOFNcpWpp6m61JsbFnE4gkt/sXSFcf3zDbmW3JOvay76Abz+Rrs
dskuAAsRo23oPQoMoRCO76Mbdc9y5O/YLAtE+8Nf8Qq8eeXQtfqqYY/T6xU4laSZ
lyDSn1KPji5oHnma03Kw64oPWtj+kLrgokVPQqlu0b/UEtLCBlKU9S5BcLOfJwn2
JQIDAQAB
-----END PUBLIC KEY-----'''


app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


def jwt_verify(token):
    valid=jwt.decode(token, public_key, algorithms=['RS256'])
    if valid:
        return True
    else:
        return False

@app.route('/api/signin',methods=['GET','POST'])
def signin():
    if request.method=='GET':
        return jsonify({"msg":"send a post request with email id and password "})
    elif request.method=='POST':
        email_id=request.form.get('email_id',None)
        username=request.form.get('username',None)
        password=request.form.get('password')
        print(email_id,username,password)
        user= User()
        
      # print(s)
        
        if email_id:
            email_check=user.sanitize(email_id)
            if not email_check:
                return jsonify({"msg":"not a valid email id"})
            userCheck=loginCollection.find_one({'email_id':email_id})
            if userCheck and pbkdf2_sha256.verify(password,userCheck['password']):
                claims={'username':userCheck['username']}
               # print('inside email')
                token=jwt.encode(claims,private_key,algorithm='RS256')
                #print(token)
                response=make_response(jsonify({"msg":"logged in via email"}))  
                response.set_cookie('jwt',token,httponly=True,secure=True)
                return response
            else:
                return jsonify({"msg":"invalid credentials"})
        if username:
            userCheck=loginCollection.find_one({'username':username})
            if userCheck and pbkdf2_sha256.verify(password,userCheck['password']):
                claims={'username':userCheck['username']}
                token=jwt.encode(claims,private_key,algorithm='RS256')
                response=make_response(jsonify({"msg":"logged in via email"}))  
                response.set_cookie('jwt',token,httponly=True,secure=True)
                return jsonify({"msg":"logged in via username"})
            else:
                return jsonify({"msg":"invalid credentials"})

        else:
            return jsonify({"msg":"error "}),500
    else:
        return jsonify({"msg":"error , method not allowed"})
        

@app.route('/api/signup',methods=['GET','POST'])
def signup():
    if request.method=='GET':
        return jsonify({"msg":"send a post request with firstname ,lastname,email id,username,password "}),200
    elif request.method=='POST':
        fname=request.form.get('firstName')
        lname=request.form.get('lastName')
        email_id=request.form.get('email_id')
        username=request.form.get('username')
        password=request.form.get('password')
        check1=loginCollection.find_one({"email_id":email_id})
        check2=loginCollection.find_one({"username":username})
        user= User()
        email_check=user.sanitize(email_id)
      # print(s)
        if not email_check:
            return jsonify({"msg":"not a valid email id"})
        if  check1==None and check2==None:
          #  print('inside')
            
            result=user.signup(fname,lname,email_id,username,password)
           # data={"firstName":fname,"lastName":lname,"email_id":email_id,"username":username,"password":password}
            loginCollection.insert_one(result)
            print(fname,lname,email_id,username,password)
            return jsonify({"msg":"account created"})
        else:
            return jsonify({"msg":"email_id already in use"})
    else:
        return jsonify({"msg":"error , method not allowed"})


@app.route('/api/products',methods=['GET']) #/api/products?id
def products():
    if request.method=='GET':
        token = request.cookies.get('jwt')
        #print(token,'from products')
        if not token:
            return jsonify({'message': 'Missing token'}), 400

        valid=jwt_verify(token)
        if valid:
            id=request.args.get('id',0)
            if int(id) in [1,2,3,4,5]:
              # print('inside if')
               data=collection.find_one({'product_id':int(id)},{"_id":0})
              # print(data)
               return data
            else:
                data=collection.find({},{"product_id": 1,"name": 1,"price": 1,"_id":0})
               # print(data)
                res = [document for document in data]
                #print(res)
                out = json.loads(json_util.dumps(res))
               # print(out)
                return out
            
            #return jsonify({"msg":"saaaa"})
        else:
            jsonify({"msg":"error , token  not valid"})
    else:
        return jsonify({"msg":"error,method not allowed"})

@app.route('/api/cart',methods=['GET','POST','DELETE'])
def cart():
    if request.method=='GET':
        token = request.cookies.get('jwt')
        if not token:
            return jsonify({'message': 'Missing token'}), 400
        valid=jwt_verify(token)
        if valid:
            data=cartCollection.find({},{"product_id":1,"name":1,"price":1,"_id":0})
            res = [document for document in data]
            out = json.loads(json_util.dumps(res))
            print(out)
            total_price = sum(item.get('price',0) for item in out)
            result = {
                "items": out,
                "total_price": total_price
                }
            return result
        else:
            return jsonify({"msg":"error , token  not valid"})
    elif request.method=='POST':
        token = request.cookies.get('jwt')
        if not token:
            return jsonify({'message': 'Missing token'}), 400
        valid=jwt_verify(token)
        if valid:
            id=request.form.get('id',0)
            if int(id) in [1,2,3,4,5]:
                find_product=collection.find_one({'product_id':int(id)},{"_id":0})
                if cartCollection.insert_one(find_product):
                    return jsonify({"msg":"product added to cart"})
                else:
                    return jsonify({"msg":"error "})
            else:
                return jsonify({"msg":"invaild product id "})
        else:
            return jsonify({"msg":"error , token  not valid"})
    elif request.method=='DELETE':
        token = request.cookies.get('jwt')
        if not token:
            return jsonify({'message': 'Missing token'}), 400
        valid=jwt_verify(token)
        if valid:
            id=request.form.get('id',0)
            if cartCollection.delete_one({'product_id':int(id)}):
                return jsonify({"msg":"product deleted from cart"})
            else:
                return jsonify({"msg":"no such product"})
        else:
            return jsonify({"msg":"error , token  not valid"})

        
    else:
        return jsonify({"msg":"error,method not allowed"})

@app.route('/api/placeOrder',methods=['GET'])
def placeOrder():
    if request.method=='GET':
        token = request.cookies.get('jwt')
        if not token:
            return jsonify({'message': 'Missing token'}), 400
        valid=jwt_verify(token)
        if valid:
            response = requests.get('http://localhost:5000/api/cart',cookies={"jwt":token})
            res=response.json()
            print(res)
            order_id=str(uuid.uuid4())

            order_doc={'order_id':order_id,'items':res.get('items',[]),'total_price':res.get('total_price',0)}
            if orderCollection.insert_one(order_doc):
                #to maintain logs
                if orderHistory.insert_one(order_doc):
                    return jsonify({'msg':'order placed successfully and added to history'}),200


                return jsonify({'msg':'order placed successfully'}),200
            else:
                return jsonify({'msg':'order failed'})
            return jsonify(res)
        else:
            return jsonify({"msg":"error , token  not valid"})
    else:
        return jsonify({"msg":"error,method not allowed"}),405

@app.route('/api/orderHistory',methods=['GET','POST'])
def orderHistoryfun():
    if request.method=='GET':
        token = request.cookies.get('jwt')
        if not token:
            return jsonify({'message': 'Missing token'}), 400
        valid=jwt_verify(token)
        if valid:
           id=request.args.get('id',0)
           print("id here:",id,type(id))
           if id==0:
                return "pass order id"
           else:
                data=orderHistory.find_one({"order_id":str(id)},{"_id":0})
                print(data)
                if data is None:
                    return {"msg":"invalid order id"}
                return (data)
        else:
            return jsonify({"msg":"error , token  not valid"})
    else:
        return jsonify({"msg":"error,method not allowed"}),405

if __name__=='__main__':
    app.run(host='0.0.0.0',port=5000)