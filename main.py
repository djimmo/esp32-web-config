import ujson

def get_configuration():
  file = open('config.json', 'r')
  configuration = ujson.loads(file.read())
  file.close()

  return configuration

def get_configuration_table(configuration):
  configTable = ''

  for key, value in configuration.items():
      if key == 'parameters':
          for parameter in value:
              if parameter['type'] == 'text':
                  configTable += """<tr><td>""" + parameter['name'] + """</td><td><input name='""" + parameter['name'] + """' type='text' value='""" + parameter['value'] + """'></td></tr>"""

              if parameter['type'] == 'number':
                  configTable += """<tr><td>""" + parameter['name'] + """</td><td><input name='""" + parameter['name'] + """' type='number' value='""" + parameter['value'] + """'></td></tr>"""

              if parameter['type'] == 'dropdown':
                  optionsHtml = str(list(map(lambda x: """<option value='""" + x['value'] + """'>""" + x['key'] + """</option>'""", parameter['options']))).strip('["]').replace('\'", "', '').strip('\'')
                  configTable += """<tr><td>""" + parameter['name'] + """</td><td><select name='""" + parameter['name'] + """'>""" + optionsHtml + """</select></td></tr>""" 
  
  return configTable

def qs_parse(qs): 
  parameters = {} 
  ampersandSplit = qs.split("&")
 
  for element in ampersandSplit: 
    equalSplit = element.split("=") 
    parameters[equalSplit[0]] = equalSplit[1] 

  return parameters

def web_page():
  if led.value() == 1:
    gpio_state="ON"
  else:
    gpio_state="OFF"
  
  html = """<!DOCTYPE html>
            <html>
              <head>
                  <title>ESP Web Config</title>
                  <meta name="viewport" content="width=device-width, initial-scale=1">
                  <link rel="icon" href="data:,">
                  <style>
                  html{
                      font-family: Helvetica;
                      display:inline-block;
                      margin: 0px auto;
                      text-align: center;
                  }
                  h1{
                      color: #0F3376;
                      padding: 2vh;
                  }
                  p{
                      font-size: 1.5rem;
                  }
                  .button{
                      display: inline-block;
                      background-color: #e7bd3b;
                      border: none;
                      border-radius: 4px;
                      color: white;
                      padding: 16px 40px;
                      text-decoration: none;
                      font-size: 30px;
                      margin: 2px;
                      cursor: pointer;
                  }
                  .button2{
                      background-color: #4286f4;
                  }

                  .configTable {
                    margin: 0 auto;
                  }

                  </style>
              </head>
              <body>
                <h1>""" + get_configuration()['title'] + """</h1>
                <p>GPIO state: <strong>""" + gpio_state + """</strong></p>              
                <div>
                  <form ... action="/" method="GET">
                    <input type="hidden" name="c" value="3" /> 
                    <table class="configTable">""" + get_configuration_table(get_configuration()) + """</table>
                    <input type="submit" value="Opslaan">
                  </form>
                </div>
              </body>
            </html>"""        

  # <p><a href="/?led=on"><button class="button">ON</button></a></p>
  # <p><a href="/?led=off"><button class="button button2">OFF</button></a></p>
   
  return html


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', 80))
s.listen(5)

while True:
  conn, addr = s.accept()
  print('Got a connection from %s' % str(addr))
  request = conn.recv(1024)
  request = str(request)
  print('Content = %s' % request)


  url = request.split(' HTTP/1.1')[0][7:]

  queryString = ''

  # At the moment only serving a page at /
  if (url.find('?') > -1):
    queryStringDict = qs_parse(url[1:])
    configuration = get_configuration()

    for configName, configValue in queryStringDict.items():
      for key, value in configuration.items():
        if key == 'parameters':
          for parameter in value:
            if parameter['name'] == configName:
              parameter['value'] = configValue
              if parameter['name'] == 'LEDON':
                parameter['value'] = configValue == 'true'
                led.value(1 if parameter['value'] else 0)

    f = open('config.json', 'w')
    f.write(ujson.dumps(configuration))
    f.close()

  response = web_page()
  conn.send('HTTP/1.1 200 OK\n')
  conn.send('Content-Type: text/html\n')
  conn.send('Connection: close\n\n')
  conn.sendall(response)
  conn.close()
