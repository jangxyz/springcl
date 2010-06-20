# language: ko

기능: 로컬 환경 구성하기
나의 생각과 아이디어를 언제 어디서나 정리하기 위해
로컬에 캐쉬를 저장하고 갱신할 수 있도록 환경을 구성해야 한다.

  시나리오: 처음에 로컬로만 초기화해서 필요한 디렉토리들을 생성한다.
    조건 <directory> 디렉토리가 안 존재한다.
    만약 로컬에서 springcl init을 하면
    그러면 <directory> 디렉토리가 존재한다.
       | directory                         |
       | @test_dir/.springcl/              |
       | @test_dir/.springcl/default/      |
       | @test_dir/.springcl/default/pages |

  #시나리오: 처음에 원격 초기화해서 필요한 디렉토리들과 기본 노트의 링크를 생성한다.
  #  조건 아무 것도 없을 때
  #  만약 원격으로 init을 하면
  #  그러면 springnote.com에 note를 주지 않고 간단한 요청을 보내서 기본 노트를 알아낸 후
  #  그리고 다음 디렉토리들이 생성하고
  #    | Directories                          | 
  #    | ~/.springcl/                         | 
  #    | ~/.springcl/DEFAULT_NOTE/            |
  #    | ~/.springcl/DEFAULT_NOTE/pages       |
  #  그리고 DEFAULT_NOTE에 대한 심볼릭 링크 default 를 만들어야 한다.

  #시나리오: 이미 내용이 있을 때 원격 초기화 하기
  #  조건 이미 다음 디렉토리들이 생성되어 있고
  #    | Directories                          | 
  #    | ~/.springcl/default/pages            | 
  #    | ~/.springcl/DEFAULT_NOTE/pages       |
  #  만약 원격으로 init을 하면
  #  그러면 springnote.com에 note를 주지 않고 간단한 요청을 보내서 기본 노트를 알아낸 후
  #  그리고 default 디렉토리에 있는 모든 페이지를 DEFAULT_NOTE 디렉토리와 병합(merge)하고
  #  그리고 DEFAULT_NOTE 에 대한 심볼릭 링크 default 를 만들어야 한다.


# vim: sts=2 et
