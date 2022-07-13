import urllib
import requests
import json
import pandas
import datetime
import uuid
from datetime import date


#### UTILS --------------------------------------------

def generate_hash_id() -> str:
  return str(uuid.uuid4())




### MAIN CLASSES -------------------------------------


class QueryString:
  
  params = dict()
  query_string = str()
  
  __params_that_need_escape = [
    'take'
  ]
  
  def __init__(self, **query_params):
    self.params = query_params
    n_params = len(query_params)
    key_value_pairs = list()
    for key, value in query_params.items():
      if key in self.__params_that_need_escape:
        key = f'${key}'
      key_value_pairs.append(f'{key}={value}')
    self.query_string = '&'.join(key_value_pairs)


  def as_string(self) -> str:
    return self.query_string



class APICommandsURI:
  
  uri = str()
  to = str()
  
  __desk_uris = [
    '/analytics/reports/attendants'
  ]
  
  __analytics_uris = [
    '/event-track'
  ]
  
  def __init__(self, uri: str, components = list()):
    self.uri = uri
    if uri in self.__desk_uris:
      self.to = 'postmaster@desk.msging.net'
    if uri in self.__analytics_uris:
      self.to = 'postmaster@analytics.msging.net'
    if self.to == '' or self.to is None:
      raise ValueError("The given URI is wrong, or, it is not supported in the available URIs in Blip API Commands.")

    if len(components) > 0:
      self.__add_components_to_uri(components)
      
    self.uri = urllib.parse.quote(self.uri)
    
    
  
  def as_string(self) -> str:
    return self.uri


  def __add_components_to_uri(self, components):
    if isinstance(components, str):
      self.uri = self.uri + '/' + components
    if isinstance(components, list):
      self.uri = '/'.join([self.uri] + components)
 



class RequestBody:
  
  id = str()
  to = str()
  method = 'get'
  uri = str()
  
  def __init__(self, uri: APICommandsURI, query_string: QueryString):
    self.id = generate_hash_id()
    self.to = uri.to
    self.uri = uri.as_string() + '?' + query_string.as_string()


  def as_dict(self) -> dict:
    body = {
      'id' : self.id,
      'to' : self.to,
      'method' : self.method,
      'uri' : self.uri
    } 
    return body

  
  def as_json_string(self) -> str:
    body = {
      'id' : self.id,
      'to' : self.to,
      'method' : self.method,
      'uri' : self.uri
    } 
    return json.dumps(body)






class RequestHeader:
  
  bot_key = str()
  content_type = str()
  
  def __init__(self, bot_key: str):
    self.content_type = 'application/json'
    self.bot_key = bot_key
    
  def as_json_string(self) -> str:
    header = {
      'Authorization' : self.bot_key,
      'Content-Type' : self.content_type
    } 
    return json.dumps(header)
  
  def as_dict(self) -> dict:
    header = {
      'Authorization' : self.bot_key,
      'Content-Type' : self.content_type
    } 
    return header  
      
    



class APICommandsRequest:
  
  body = str()
  header = str()
  response = str()
  
  def __init__(self, body: RequestBody, header: RequestHeader):
    self.body = body.as_json_string()
    self.header = header.as_dict()
    self.response = requests.post(
      'https://msging.net/commands',
      self.body,
      headers = self.header
    )

  def get_response_content(self) -> dict:
    return self.response.json()
    

  def to_pandas_dataframe(self) -> pandas.DataFrame:
    content = self.response.json()
    items = content['resource']['items']
    dataframe = pandas.DataFrame.from_dict(items)
    return dataframe






#### FUNCTIONS FOR REQUESTS -------------------------

## URI: /analytics/reports/attendants
def get_attendants_report(
                       botKey: str,
                       startDate: datetime.date, endDate: datetime.date
                     ) -> pandas.DataFrame:
                       
  header = RequestHeader(botKey)
  query_string = QueryString(beginDate = startDate, endDate = endDate)
  uri = APICommandsURI('/analytics/reports/attendants')
  body = RequestBody(uri, query_string)
  
  request = APICommandsRequest(body, header)
  results = request.to_pandas_dataframe()
  
  return results




## URI: /event-track
def get_event_track(
                     botKey: str, tracking: str,
                     startDate: datetime.date, endDate: datetime.date,
                     take = 500, action = None
                   ) -> pandas.DataFrame:
                     
  if action is None:
    components = tracking
  else:
    components = [tracking, action]
    
  if action is not None and take > 500:
    raise ValueError("When you define an action to be searched, the `take` argument can not be greater than 500. If you want use more than 500 in `take`, then, do not specify the `action` argument.")
                     
  uri = APICommandsURI('/event-track', components)
  header = RequestHeader(botKey)
  query_string = QueryString(startDate = startDate, endDate = endDate, take = take)
  body = RequestBody(uri, query_string)
  
  request = APICommandsRequest(body, header)
  results = request.to_pandas_dataframe()
  
  return results



