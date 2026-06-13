Feature: Dashboard DynamoDB persistence

  Scenario: Round-trip preserves title
    Given a dashboard titled "Sales Overview"
    When the dashboard is saved
    And the dashboard is reloaded by its ID
    Then the reloaded dashboard title is "Sales Overview"

  Scenario: Round-trip preserves tile position
    Given a saved question
    And a dashboard with a tile for that question at row 1 col 2 width 4 height 3
    When the dashboard is saved
    And the dashboard is reloaded by its ID
    Then the reloaded dashboard has 1 tile
    And the tile position is row 1 col 2 width 4 height 3

  Scenario: Round-trip links tile back to its question
    Given a saved question
    And a dashboard with a tile for that question at row 0 col 0 width 4 height 2
    When the dashboard is saved
    And the dashboard is reloaded by its ID
    Then the tile is linked to the original question ID

  Scenario: Round-trip preserves filter bindings
    Given 2 saved questions
    And a dashboard with tiles for both questions
    And a filter from tile 1 on column "region" targeting tile 2
    When the dashboard is saved
    And the dashboard is reloaded by its ID
    Then tile 1 filters tile 2 on column "region"

  Scenario: Loading a missing ID returns None
    When a random dashboard ID is loaded
    Then the dashboard result is None

  Scenario: Empty dashboard reloads with no tiles
    Given an empty dashboard
    When the dashboard is saved
    And the dashboard is reloaded by its ID
    Then the reloaded dashboard has 0 tiles
