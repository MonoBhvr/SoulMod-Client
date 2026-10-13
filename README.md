# SoulMod-Client

GameMaker(VM) 게임 모드를 위한 새 클라이언트. 원본 `data.win`을 건드리지 않고,
`data.win` 전체를 메모리에 올려 패치하지도 않는다. 여러 형식의 모드를 공용
모드 형태로 정규화한 뒤, 런타임에 전달되는 스크립트를 가로채 적용한다.
언더테일·델타룬을 비롯한 같은 형식 GameMaker 게임의 다중 게임 모드를 지원하고,
여러 모드를 안정적으로 함께 적용·관리하는 것을 목표로 한다.

구 UTDT-SoulMod 트리는 기술 참고용으로만 썼다. 실행 복사·패치·복원 파이프라인은
이 클라이언트에 들어오지 않는다.

## 구조

```text
new-client/
  src/soulmod_client/
    normalizer.py    # 형식별 모드 -> 공용 v1 ops
    registry.py      # UT/델타룬 게임 매트릭스
    interceptor.py   # 스크립트 전달 갈고리 런타임(파일 IO 없음)
    resolver.py      # 다중 모드 결정론적 해석, 충돌 시 fail-closed
    manager.py       # 설치/활성/프로파일
  cli.py             # normalize / apply-demo / multi-demo
  tests/             # 수직 슬라이스 테스트
```

## 실행

```sh
python new-client/tests/test_vertical_slice.py -v
python new-client/cli.py normalize <strings.json> <modId> <out.json>
python new-client/cli.py apply-demo <strings.json> <modId> <gameId> <data.win> <evidenceDir>
python new-client/cli.py multi-demo <a.json> <modA> <b.json> <modB> <gameId> <data.win> <evidenceDir>
```

## 원칙

- 설치된 게임 파일 불변. `data.win`은 읽기 전용 해시 확인에만 쓴다.
- 공용 폼은 v1 manifest+operations와 호환된다.
- 충돌은 병합하지 않고 설치 전에 막는다(중복 동일 값은 1개만 유지).
