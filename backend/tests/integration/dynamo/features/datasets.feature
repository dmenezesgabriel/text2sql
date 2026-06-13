Feature: Dataset DynamoDB persistence

  Scenario: Round-trip preserves name and location
    Given a dataset named "sales" of kind TABLE at "s3://bucket/sales.parquet"
    When the dataset is saved
    And the dataset is reloaded by its ID
    Then the reloaded dataset name is "sales"
    And the reloaded dataset location is "s3://bucket/sales.parquet"

  Scenario: Round-trip preserves schema columns
    Given a dataset with a column "revenue" of type "DOUBLE"
    When the dataset is saved
    And the dataset is reloaded by its ID
    Then the reloaded schema has 1 column
    And the first column is "revenue" of type "DOUBLE"

  Scenario: Loading a missing ID returns None
    When a random dataset ID is loaded
    Then the dataset result is None

  Scenario: Delete removes the record
    Given a saved dataset
    When the dataset is deleted
    And the dataset is reloaded by its ID
    Then the dataset result is None

  Scenario: Find all returns every saved dataset
    Given 3 saved datasets
    When all datasets are listed
    Then 3 datasets are returned
