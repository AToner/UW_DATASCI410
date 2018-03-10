# General notes

The project write up is in the notebook "Final Project Analysis.ipynb"

# Twitter Info

## Application Workflow
https://developer.twitter.com/en/docs/basics/authentication/overview/application-only

## Twitter search API
https://developer.twitter.com/en/docs/tweets/search/api-reference/get-search-tweets.html

## Library Information

* https://github.com/bear/python-twitter
* https://python-twitter.readthedocs.io/en/latest/twitter.html#module-twitter.api

# Geography
http://boundingbox.klokantech.com/

Cities used (closest airport)

* Seattle -122.459696,47.491912,-122.224433,47.734145 (US/KSEA)
* New York -74.077185,40.679108,-73.850592,40.839301 (US/KJFK)
* Manchester, UK -2.363539,53.399903,-2.123899,53.554376 (UK/EGCC)
* Sydney, AUS 150.919615,-34.001366,151.338469,-33.733399 (AU/YSSY)

# AWS 

## Sentiment detection
https://docs.aws.amazon.com/comprehend/latest/dg/API_DetectSentiment.html    

# Weather

## Wunderground

Example history... 
* http://api.wunderground.com/api/[api_key]/history_20180122/q/AUS/YSSY.json
* http://api.wunderground.com/api/[api_key]/history_20180122/q/UK/EGCC.json

## World Climate
### 24 Hour Average Temperature

http://www.worldclimate.com/  
Manchester Airport - http://www.worldclimate.com/cgi-bin/data.pl?ref=N53W002+1102+03334W  

[37.6, 39.2, 42.1, 46.6, 52.9, 57.9, 60.4, 60.1, 56.1, 50.2, 43.0, 39.7]

Seattle Airport - http://www.worldclimate.com/cgi-bin/data.pl?ref=N47W122+1302+457473C  

[40.1, 43.3, 45.5, 49.1, 55.0, 60.8, 65.1, 65.5, 60.4, 52.7, 45.1, 40.5]

JFK Airport - http://www.worldclimate.com/cgi-bin/data.pl?ref=N40W073+1302+305803C  

[31.3, 32.9, 41.0, 50.4, 59.9, 69.3, 75.4, 74.7, 67.5, 56.8, 47.1, 36.5]

Sydney Airport - http://www.worldclimate.com/cgi-bin/data.pl?ref=S33E151+1102+94767W  

[71.8, 71.6, 69.6, 64.9, 59.4, 55.0, 53.2, 55.4, 59.4, 63.7, 66.9, 70.2]

