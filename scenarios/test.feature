Feature: Testing
    Scenario: Near a point in space
        When I am within 100 meters of "[0,0]"
        Then ping "http://localhost:5000/fhjkdsfds"
