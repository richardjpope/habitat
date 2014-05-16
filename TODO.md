
    apps know when auth expired (cant do this until flask restful fixed)
  - setup
  - get deployed
  - get location app on phone
    copy config over to template
  - cards
  - add 'does not have permission to'
  - add placename to location model
- - validate scopes
- - Review admin user session. Currently uses simple session login.
  - vary image
  - add image attribution
  - add stats to homepage
  - seperate testing config
  - make sure all time gets converted to UTC on save / query
  - only fire events once  
  - handle no secret properly

DONE:
- make token expiry configerable
- ability to delete token
- location api should return geojson points
- tidy up confirmation page
- rename latlng to lnglat
- ping a url when near a location



THOUGHTS:

scenario plus variables

Given a scenarios has run successfully, decide if the Then task should be completed? or is valid?
------

hash of the scenario

hash of the 'when(s)'

when plus a time/space block out e.g. hash of hour plus n digits of area

each step defines a function that specifies how often it can be done. e.g. 'within 100 meters' has somehting that says 'only if not been there before'

sanity checking number fo things sent
