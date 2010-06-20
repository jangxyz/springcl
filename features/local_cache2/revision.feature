Feature: read & write local cache with revision operation
In order to organize my thoughts and ideas better
by keeping track of change of the page through time,
I should read revisions of page locally

  Scenario: reading revision of page locally reads from cache
    Given a cached revision of page
    When  I locally read a revision of page <page id> with revision id <rev id> from note <note> in format <format> 
    Then  it reads content from ./springcl/<note2>/pages/<page id>/revisions/<rev id>/<format2>


  Scenario: reading revision of page remotely creates new cache
    Given nothing
    When  I remotely read a revision of page <page id> with revision id <rev id> from note <note> in format <format> 
	Then  it fetches the revision from springnote.com
    And   saves fetched data in ./springcl/<note>/pages/<page id>/revisions/<rev id>/<format>
	And   shows data


    Examples:
        | note    | note2   | page id | rev id | format | format2 | 
        | jangxyz | jangxyz | 563954  | 806237 | json   | json    | 
        | diary   | diary   | 317209  | 123456 |        | json    | 
        |         | default | 317209  | 123456 |        | json    | 
    # other formats: NOT YET
  
  #Scenario: reading revision by index locally
  
# vim: sts=2 et
