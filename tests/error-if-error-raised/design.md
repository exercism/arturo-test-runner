# Design Rationale

If an error is raised during any test, Unit 3.0.0 exports an empty `specs` block in `.unitt/tests/test-<slug>.art`.
This means even if other tests ran successfully before this point, we don't know whether they passed or not.
The entire test suite as a result needs to be errored out with the message being Arturo's stdout.
