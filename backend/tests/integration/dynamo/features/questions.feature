Feature: Question DynamoDB persistence

  Scenario: Round-trip preserves viz format
    Given a question with TABLE viz format
    When the question is saved
    And the question is reloaded by its ID
    Then the reloaded viz format is TABLE

  Scenario: Round-trip preserves viz props
    Given a question with viz props {"color": "red", "size": 42}
    When the question is saved
    And the question is reloaded by its ID
    Then the reloaded viz props are {"color": "red", "size": 42}

  Scenario: Round-trip preserves viz children
    Given a question with viz children ["child1", "child2"]
    When the question is saved
    And the question is reloaded by its ID
    Then the reloaded viz children are ["child1", "child2"]

  Scenario: Loading a missing ID returns None
    When a random question ID is loaded
    Then the question result is None

  Scenario: Delete removes the record
    Given a saved question
    When the question is deleted
    And the question is reloaded by its ID
    Then the question result is None

  Scenario: Find all returns every saved question
    Given 3 saved questions
    When all questions are listed
    Then 3 questions are returned
