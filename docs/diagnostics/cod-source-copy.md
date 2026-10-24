# Fresh diagnostic repository

At the user's request, a new source destination was prepared without deleting or renaming the original fork.

GitHub's fork API accepted the request but returned the existing R347H4CK3R/madeira fork, not a second fork in the same account/network. The connected account has no available organization destination.

A separate public repository was therefore created as an explicitly labeled independent source copy:

https://github.com/R347H4CK3R/madeira-cod-test

Verified repository ID: 1431827019; fork=false. This is not a second GitHub fork and is not a public binary release. Original fork/main and previous builds remain untouched.

The full tested source history was pushed on fix/cod-1938090-ipa-20261024 at 3b7a7617be280ce3a4dece1704e6c4a48c16ca92, preserving upstream authorship, license texts, pinned submodules and diagnostic patches. Native compilation and device tests remain required. Actions execution eligibility is being checked independently; an enabled repository setting alone does not establish execution eligibility.
