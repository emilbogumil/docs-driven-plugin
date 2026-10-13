# Gherkin companion to test-cases.md. Tags: the first tag is the case ID, the
# following tags are the requirements it covers.
Feature: {{title}}

  @{{code}}-T01 @{{code}}-R01
  Scenario: <case title>
    Given <precondition>
    When <action>
    Then <expected>
