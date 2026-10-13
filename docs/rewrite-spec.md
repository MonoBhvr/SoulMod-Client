# Rewrite spec

## 목표
여러 형식(xdelta, csx, patched data.win, UndertaleMod 파생)의 모드를 공용 모드
형태로 재작성하고, 런타임에 전달되는 스크립트를 가로채 적용한다. 실제
`data.win`을 건드리지 않고, 모든 `data.win`을 메모리에 올리고 패치하지 않고
모드를 적용한다. GameMaker 다중 게임 모드를 지원해 델타룬도 동작한다.
최종 목표는 언더테일·델타룬과 같은 형식으로 빌드된 GameMaker 게임의 모드들을
여러 개 안정적으로 적용하고 이를 관리하는 애플리케이션이다.

## 아키텍처
mods(각 형식) -> Normalizer -> 공용 v1 -> Resolver -> InterceptRuntime
-> 게임(스크립트 전달 갈고리), GameRegistry(UT/델타룬 매트릭스),
ManagerApp(설치·프로파일·충돌 안내, 설치본 손대지 않음).

## 보장
Zero-Modification: 디스크의 `data.win`은 읽기 전용. 임시 win 파일을 만들지
않는다. 지문 불일치·비정상 모드·경로 탈출·미지원 op는 형식 오류로 닫고
부분 적용을 남기지 않는다.

## 상태
- C1 정규화, C2 무터치 적용, C3 멀티게임 해석, C4 fail-closed 증명 완료.
- 다음: 포맷별 normalizer 레인, 게임별 native intercept, 매니저 앱.
