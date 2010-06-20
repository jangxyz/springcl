기능: 로컬 캐쉬에 댓글(comments) 읽고 쓰기
  다른 사용자들의 댓글을 읽음으로써
  페이지의 내용을 질적으로 향상시키기 위해
  로컬에서도 페이지에 달린 댓글들을 읽을 수 있어야 한다.

  시나리오: 캐쉬에 있는 댓글을 로컬로 리스트한다.
    조건   페이지에 달린 댓글의 캐쉬가 존재할 때
    만약   로컬로 <page id> 페이지의 댓글을 <format> 형식으로 리스트하면
    그러면 경로 ./springcl/<note2>/pages/<page id>/comments/ 에서 모든 *.<format> 파일을 찾아서 읽는다.

    예:
        | note    | note2   | page id | format | format2 | 
        | jangxyz | jangxyz | 563954  | json   | json    | 
        | diary   | diary   | 317209  |        | json    | 
        |         | default | 317209  |        | json    | 

# vim: sts=2 et
