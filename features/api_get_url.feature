Feature: Api get URL
    Get json from api

    Scenario: Empty URL
        When I press "ctrl+l"
	And I press "enter"

	Then I see "Url is required" on screen
