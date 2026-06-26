# Behavior-Driven Development (BDD) Specification
# Source of Truth: validate_ingestion node behavior in ingestion.py.
# Any changes to ingestion.py must satisfy all scenarios defined in this document.

Feature: Ingestion Validation and Parsing
  As an AI-powered technical interview coach
  I want to validate that the candidate has provided a CV (via text paste or PDF upload) and target job role
  So that I can extract accurate claims and generate grounded, role-specific questions.

  Scenario: Happy path - User uploads a PDF CV and target job role is provided
    Given the candidate session has no prior state
    And the candidate uploads a valid PDF CV
    And the candidate provides a target job role
    When the validate_ingestion node executes
    Then the node should successfully parse the PDF CV text
    And the node should yield a "valid" route
    And the node should output the parsed CV text, target job role, and any project documentation
    And the session state should store the cv_text, role, and parsed_pdf name

  Scenario: Missing target job role - User uploads PDF CV but no role is provided
    Given the candidate session has no prior state
    And the candidate uploads a valid PDF CV
    And the candidate does not provide a target job role
    When the validate_ingestion node executes
    Then the node should successfully parse the PDF CV text
    And the node should yield a state-updating Event to persist cv_text and parsed_pdf name in the session state
    And the node should yield a RequestInput asking the candidate for the "Target Job Role"
    And the CV text must be preserved in the session state before the pause

  Scenario: Missing CV - User provides target job role but no CV is provided
    Given the candidate session has no prior state
    And the candidate provides a target job role
    And the candidate has not pasted a CV or uploaded a PDF CV
    When the validate_ingestion node executes
    Then the node should yield a state-updating Event to persist the target job role in the session state
    And the node should yield a RequestInput asking the candidate for their "CV/Resume"
    And the target job role must be preserved in the session state before the pause

  Scenario: Resume after pause - User provides missing information
    Given the candidate session has previously paused with CV text in the session state
    And the target job role was missing in the previous turn
    When the candidate responds with the missing target job role
    And the validate_ingestion node resumes execution
    Then the node should retrieve the previously parsed CV text from the session state
    And the node should parse the new conversational input to extract the target job role
    And the node should successfully transition to the "valid" route with all materials intact

  Scenario: PDF parsing failure - Uploaded PDF cannot be parsed
    Given the candidate session has no prior state
    And the candidate uploads a corrupted or unreadable PDF CV
    When the validate_ingestion node executes
    Then the node should catch the parsing exception gracefully
    And the node should not crash
    And the node should yield a RequestInput prompting the candidate to paste their CV as text instead
