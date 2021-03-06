Feature: Error handling
    Errors occuring when working with url

    Background:
	Given I focused url field

    Scenario: Empty URL
	When I press "enter"

	Then I see "Url is required" on screen

    Scenario: Invalid URL
	When I write "htt"
	And I press "enter"

	Then I see "Invalid URL" on screen

	When I press "escape"

	Then I don't see "Invalid URL" on screen

    Scenario: Connection Error
	Given server responds with error

	When I write "http://localhost/"
	And I press "enter"

	Then I see "Connection Error" on screen
