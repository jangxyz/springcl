기능: 로컬 캐쉬에 첨부파일(attachments) 읽고 쓰기 - download/upload files even when I'm offline
  why? so i could be synced with the server on important files 
  why? so i could 

  #
  #
  #
  시나리오: 캐쉬에 있는 첨부파일의 메타정보를 읽는다.
    조건 페이지에 달린 첨부파일의 메타정보가 캐쉬에 있을 때
    만약 로컬로 <page id> 페이지의 첨부파일 <attachment id>의 메타정보를 <format> 형식으로 읽으면
    그러면 경로 ./springcl/<note2>/pages/<page id>/attachments/<attachment id>/<format> 파일 내용을 보여준다.

  시나리오: 캐쉬에 있는 첨부파일 내용을 읽는다.
    조건 페이지에 달린 첨부파일의 내용이 캐쉬에 있을 때
    만약 로컬로 <page id> 페이지의 첨부파일 <attachment id>의 내용을 읽으면
    그러면 경로 ./springcl/<note2>/pages/<page id>/attachments/<attachment id>/file 파일 내용을 보여준다.

  #
  #
  #
  시나리오: 원격으로 첨부파일의 메타정보를 읽으면 메타정보아 내용 모두를 캐쉬에 저장한다.
    조건 페이지에 달린 첨부파일의 메타정보가 캐쉬에 없을 때
    만약 원격으로 <page id> 페이지의 첨부파일 <attachment id>의 메타정보를 <format> 형식으로 읽으면
    그러면 springnote.com 에서 첨부파일의 메타정보아 내용을 읽어와서
    그리고 경로 ./springcl/<note2>/pages/<page id>/attachments/<attachment id>/<format>에 메타정보를 저장하고
    그리고 경로 ./springcl/<note2>/pages/<page id>/attachments/<attachment id>/file 에 내용을 저장하고


    예:
        | note    | note2   | page id | attachment | format | format2 | 
        | jangxyz | jangxyz | 563954  |  1234567   | json   | json    | 
        | diary   | diary   | 317209  |  3456789   |        | json    | 
        |         | default | 317209  |  1111111   |        | json    | 
# vim: sts=2 et
