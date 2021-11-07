Feature: Search in data

    Background:
        Given server responds with data
            {
                "ala1": 1,
                "ala2": 2
            }
        Given I focused url field
        Given I wrote "http://localhost/"
        Given I pressed "enter"

    Scenario: Basic search 
        When I press "/"
        And I write "ala"
        And I press "enter"

        Then I see "N.*Next" on screen
        And I see "1;31;43mala.*?m1.*?:.*?m1" on screen

        When I press "n"

        Then I see "1;31;43mala.*?m2.*?:.*?m2" on screen

    Scenario: Cancel search
        When I press "/"
        And I write "ala"
        And I press "enter"
        And I press "escape"

        Then I don't see "1;31;43mala.*?m1.*?:.*?m1" on screen


