import requests
import qrcode


data = {'message':'hola puto','phone':'5493874842388'}


try:
    resp = requests.post('http://demo.blackfishweb.com:8080/getqr', json=data)
    resp = resp.json()
    print(resp)
except:
  print("SERVIDOR CAIDO")


