------

Thick-Denim ``0.1.0``
=====================

**Command-line application to gather data and produce metrics from API calls to JIRA and Github**



Etymology
---------

JIRA in spanish `means <https://en.wiktionary.org/wiki/jira#Noun>`_ *"large piece torn from a fabric."*

The project goal is to calculate work from JIRA + GITHUB, so we could say it's our "work fabric".

Denim was invented by Levi Strauss as a sturdy fabric to build clothes
for workers. Construction workers used think jeans to protect their
skin.

That's why we got "Thick-Denim".


How to contribute:
------------------


1. Make sure `poetry is installed <https://poetry.eustace.io/docs/#installation>`_.
2. Clone this repo
3. Run the commands below


.. code:: bash

   make dependencies
   make tests

API Test Tokens
---------------


- **JIRA:** `https://id.atlassian.com/manage/api-tokens <https://id.atlassian.com/manage/api-tokens>`_
- **GITHUB:** `https://github.com/settings/tokens <https://github.com/settings/tokens>`_


How VCR tests work
------------------


1. decorated `@vcr.use_cassette` test execute
2. An API call is made with a  real TOKEN
3. response is retrieved and test passes
