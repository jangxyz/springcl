Feature: updating local cache with page operation
why? so I could read & write page resources locally and sync later
why? because page is the most important resource on organizing my thoughts and ideas

#read / list / create / update / delete
#page / revision / comment / attachment
#update / merge / conflict

  Scenario: local page read shows from cache
	Given a cached page
	When  I locally read a page PAGEID from NOTE in FORMAT
	Then  it reads the page from ./springcl/NOTE/pages/PAGEID/FORMAT

  Scenario: remote page read creates cache and shows content
	Given there is no directory ./springcl/NOTE/pages/PAGEID/
	When  I read a page with pageid PAGEID from note NOTE remotely
	Then  it fetches the page from springnote.com
	And   creates a directory on ./springcl/NOTE/pages/PAGEID/
	And   saves fetched data in format FORMAT to ./springcl/NOTE/pages/PAGEID/FORMAT
	And   shows the page

  Scenario: remote page read updates cache and shows content
	Given there is a directory ./springcl/NOTE/pages/PAGEID/
	When  I read a page with pageid PAGEID from note NOTE remotely
	Then  it fetches the page from springnote.com
	And   saves fetched data in format FORMAT to ./springcl/NOTE/pages/PAGEID/FORMAT
	And   shows the page



# vim: sts=2
