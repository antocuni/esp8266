import http_server
import machine

RELAY = machine.Pin(5, machine.Pin.OUT)

HTML = b"""\
HTTP/1.0 200 OK

<html>
  <head>
<meta name="viewport" content="width=device-width, initial-scale=1, maximum-scale=1, minimum-scale=1, user-scalable=no, minimal-ui">

    <style>
/* The switch - the box around the slider */
.switch {
  position: relative;
  display: inline-block;
  width: 60px;
  height: 34px;
}

/* Hide default HTML checkbox */
.switch input {display:none;}

/* The slider */
.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #ccc;
  -webkit-transition: .4s;
  transition: .4s;
}

.slider:before {
  position: absolute;
  content: "";
  height: 26px;
  width: 26px;
  left: 4px;
  bottom: 4px;
  background-color: white;
  -webkit-transition: .4s;
  transition: .4s;
}

input:checked + .slider {
  background-color: #2196F3;
}

input:focus + .slider {
  box-shadow: 0 0 1px #2196F3;
}

input:checked + .slider:before {
  -webkit-transform: translateX(26px);
  -ms-transform: translateX(26px);
  transform: translateX(26px);
}

/* Rounded sliders */
.slider.round {
  border-radius: 34px;
}

.slider.round:before {
  border-radius: 50%%;
}
    </style>
    
  </head>
  <body>
    <h1>Relay</h1>
    <form id="myform" action="">
      <label class="switch">
        <input name="relay" %s type="checkbox" onchange="this.form.submit()">
        <span class="slider round"></span>
      </label>
    </form>
  </body>
</html>
"""


def handler(req):
    if 'GET /favicon.ico' in req:
        return ""

    if 'GET /?relay=on' in req:
        RELAY.on()
        status = "checked"
    else:
        RELAY.off()
        status = ""
    
    response = HTML % status
    return response

http_server.serve_forever(handler)
