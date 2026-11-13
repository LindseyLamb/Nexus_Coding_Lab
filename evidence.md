# Nexus lab evidence

## Contributors and participation
Names; who typed, traced behavior, designed or checked tests. Ad hoc groups are fine.
Brennan Romero - typed, traced behavior, designed one of the tests.
Lindsey Lamb - Designed one of the tests, checked tests, helped catch missing things/errors.

## Baseline
Pinned upstream: 75a8d145aa5bc0c92725197c0e4e9883491c542f.
Interpreter/version, command, actual output. Expected starter: four passes, four failures.
Python version 3.14.7

## Our design decision
Audit owner and interface; ordering; one credible alternative; accepted benefit/cost.
We decided to add an auditor.py file and added an audit subscriber and subscribed to a newly 
allocated audit channel. Created a temp file to hold that file during the test suite. Ordering: 
lifecycle services validates the command, then publishes the audit event, marks the customer as 
inactive and saves before finally publishing the general event that triggers the delivery of the
notification. Benefit: This keeps confidential audit data from general event subscribers and keeps 
the existing structure. It also allowed the audit storage implementation to be changed through a 
common interface. Accepted Cost: We have both channels being managed by EventBus. This makes 
routing more complex and only provides logical separation rather than a more secure boundary.
Also our file-backed implementation adds some storage and lifecycle concerns. Alternatives: We could've done a direct audit collaborator inside of CustomerLifecycleService. 

## Actual changes
Changed files/functions. What is implemented versus still proposed?
Explain the sanctioned original notification-test expectation change.
We changed services.py, events.py, notifications.py, errors.py, adapter.py, test_contract.py, 
test_lifecycle.py.  - All implemented - Don't believe that we have anything still waiting from the
proposal. The sanctioned test expectation change was changing the message expected to "Your Atlas 
account has been deactivated." This was done because the implementation changed and the original 
notification test did not account for that change. 

## Our added behavior check
Conditions, action, expected observable result and reason for choosing it.
We added to behavior checks. One was to make sure that the reason was private - Condition: a 
second subscriber is registered on the general event channel. Action: Authorized deactivation 
command is given that has a reason. Expected observable result: The new subscriber receives the 
deactivation event with the customer ID and email but without the reason and the audit record 
retains the reason. Reason: We needed to keep confidential audit events from general subscribers
and checking to make sure the second subscriber does not receive the information gives us evidence 
that the boundary is secure.  
The second test was to make sure that the file saved and resumes correctly. Condition: A JSON 
audit file contains one record. Action: A FileBackedAudit instance loads the file, and a new 
deactivation record is added. Expected observable result: Calling getRecords returns both the 
original record and the newly added record. Reason: We wanted to make sure that the file-backed 
implementation could load existing audit information and retain it while adding new records.

## Final execution evidence
Command and actual output. Separate the lab runner from the original pytest suite.
If a command was not run, say so. Preserve remaining failures and their meaning.


@LindseyLamb ➜ /workspaces/Nexus_Coding_Lab/nexus2 (main) $ python run_lab.py
test_01_reason_stays_out_of_public_event (test_contract.Contract.test_01_reason_stays_out_of_public_event) ... ok
test_02_customer_gets_generic_notification (test_contract.Contract.test_02_customer_gets_generic_notification) ... ok
test_03_reason_is_retained_in_internal_audit (test_contract.Contract.test_03_reason_is_retained_in_internal_audit) ... ok
test_04_success_preserves_customer_result (test_contract.Contract.test_04_success_preserves_customer_result) ... ok
test_05_denied_command_has_no_effects (test_contract.Contract.test_05_denied_command_has_no_effects) ... ok
test_06_short_reason_has_no_effects (test_contract.Contract.test_06_short_reason_has_no_effects) ... ok
test_07_missing_customer_has_no_effects (test_contract.Contract.test_07_missing_customer_has_no_effects) ... ok
test_08_notification_failure_does_not_erase_audit (test_contract.Contract.test_08_notification_failure_does_not_erase_audit) ... ok
test_09_second_public_subscriber_cannot_see_reason (test_contract.Contract.test_09_second_public_subscriber_cannot_see_reason) ... ok
test_10_filebacked_audit_resumes (test_contract.Contract.test_10_filebacked_audit_resumes) ... ok

----------------------------------------------------------------------
Ran 10 tests in 0.014s
@LindseyLamb ➜ /workspaces/Nexus_Coding_Lab/nexus2 (main) $ pytest
.......................                                                                                       [100%]
23 passed in 0.07s

## Limitations and next step
What do the results not establish? What would you check next?
We don't have anything about write failures and no established about crashes or other errors do to 
the audit logs. We would want to check behaviors and possible establish requirements for what 
would happen there and how it would effect implementation.

## Individual PR starting points
Each person separately: initial claim, consequential challenge, current disposition.
Copy the shared code/evidence before leaving. No submission is due at class end.
