Feature: Autocomplete recent urls
    Background:
        Given server responds with data
            {}
        And url "http://localhost/" was used in the past
        And I focused url field

    Scenario: Show recent urls
        When I write "htt"
        And log screen

        Then I see "http://localhost/" on screen
        
        When I press "escape"

        Then I don't see "http://localhost/" on screen

    Scenario: Moving around recent urls
        Given url "http://localhost:5000/" was used in the past

        When I write "htt"
        And I press "down"

        Then url "http://localhost/" is selected

        When I press "down"

        Then url "http://localhost:5000/" is selected

        When I press "down"

        Then url "http://localhost/" is selected

        When I press "up"
        
        Then url "http://localhost:5000/" is selected

