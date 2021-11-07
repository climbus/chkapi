Feature: Show data from url

	Background:
		Given I focused url field

	Scenario: Show json data
		Given server responds with data
		    {"a": 1}

		When I press "ctrl+l"
		And I write "http://localhost/"
		And I press "enter"

		Then I see "{[[\s\S]+\"a\"[\s\S]+:[\s\S]+1[\s\S]+}" on screen

	Scenario: Show headers
		Given server responds with headers
            {
            "Header1": "val 1",
            "header-2": "val 2"
            }

		When I write "http://localhost/"
		And I press "enter"
		And I press "h"

		Then I see "Header1.*val 1" on screen
		Then I see "header-2.*val 2" on screen

		When I press "escape"

		Then I don't see "Header1.*val 1" on screen
		Then I don't see "header-2.*val 2" on screen
