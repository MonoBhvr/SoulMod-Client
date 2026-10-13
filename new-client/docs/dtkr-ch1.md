# DTKR 개요 (챕터 1)

`SoulMod.UmtWorker` v5 diff(스팀 최신 `data.win` 대 패치 복사본) + `lang_ja.json` 직접
검증으로 확정한 한글패치 실체. data.win을 건드리지 않고 인터셉트로 재현한다.

- 문자열 6241개: `언어파일들/chapter1_windows/lang/lang_ja.json` 6242개 중 `date`
  제외. 한글 포함 5473개, `^N`/`%`/`\M1` 제어코드 포함 3270개. 키 주소 지정이라
  원문 전제조건 없음.
- 폰트 7종: 교체 6(fnt_ja_comicsans, dotumche, main, mainbig, small,
  tinynoelle) + 추가 1(fnt_ja_legend). 범위 끝 55203 = 한글 전체 커버.
  `font.register` op + 아틀라스 바이트 해시 검증.
- 스프라이트 22개: 일어 baked 텍스트(bg_lang_ja_* 5, spr_ja_* 17) 교체.
  `sprite.replace` op, 스테이징 PNG 바이트 해시 검증.
- 코드 9개 추가: scr_get_josa, scr_is_hangul, scr_jamo_join, scr_jamo_split
  (+ GlobalScript 중복, subst-string anon 1). 실행 op로 내보내지 않고
  `review.json` ManualReviewRequired로만 기록한다.
- 텍스처 페이지 보고서 156개: 폰트/스프라이트 아틀라스 재빌드 부산물. 새
  클라이언트는 아틀라스를 만지지 않으므로 op로 만들지 않는다.

재현: `cli.py dtkr-build <lang_ja.json> <result.json> <stage> <mod> <game> <out>`
에셋 29개 sha256 대조 통과. DTKR 원본 에셋은 레포에 넣지 않고 로컬에서만
빌드한다.
