Feature: Show data from url
    Scenario: Show json data
		Given server responds with data
		    {"a": 1}

		When I press "ctrl+l"
		And I write "http://localhost/"
		And I press "enter"

		Then I see "{[[\s\S]+\"a\"[\s\S]+:[\s\S]+1[\s\S]+}" on screen
