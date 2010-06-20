# language: ko

기능: 로컬 캐쉬에 페이지(page) 읽고 쓰기
  나의 생각과 아이디어를 그때그때 정리하기 위해
  페이지를 로컬로도 읽고 쓸 수 있어야 한다.

  시나리오 개요: 캐쉬에 있는 페이지를 로컬로 읽는다.
    조건 페이지의 캐쉬가 존재할 때
    만약 로컬로 <note> 노트의 <page id> 페이지를 <format> 형식으로 읽으면
    그러면 경로 ./springcl/<note2>/pages/<page id>/<format2> 를 읽는다.

	예:
        | note    | note2   | page id | format | format2 | 
        | jangxyz | jangxyz | 563954  | json   | json    | 
        | diary   | diary   | 317209  |        | json    | 
        |         | default | 317209  |        | json    | 

  시나리오 개요: 원격으로 페이지를 읽어와서 캐쉬를 새로 생성한다.
    조건 페이지의 캐쉬가 안 존재할 때
    만약 원격으로 <note> 노트의 <page id> 페이지를 <format> 형식으로 읽으면
    
    그러면 springnote.com 에서 페이지의 내용을 읽어와서
    그리고 경로 ./springcl/<note2>/pages/<page id>/<format2> 에 내용을 저장하고
    그리고 내용을 보여준다.

	예:
        | note    | note2   | page id | format | format2 | 
        | jangxyz | jangxyz | 563954  | json   | json    | 
        | diary   | diary   | 317209  |        | json    | 
        |         | default | 317209  |        | json    | 

  #시나리오: 원격으로 페이지를 읽어와서 캐쉬를 갱신(update)한다.
  #시나리오: 원격으로 페이지를 읽어와서 캐쉬를 병합(merge)한다.
  #시나리오: 원격으로 페이지를 읽어와서 캐쉬와의 충돌(conflict)을 해결한다.



#read / list / create / update / delete
#page / revision / comment / attachment
#update / merge / conflict

# vim: sts=2
