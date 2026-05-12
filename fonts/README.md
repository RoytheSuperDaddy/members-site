# Fonts 폴더 안내

이 폴더에 다음 2개 폰트 파일을 배치해야 합니다:

```
fonts/
├── SamsungGothicLong-Regular.ttf      (font-weight: 400)
└── SamsungGothicLong-UltraLight.ttf   (font-weight: 200)
```

## 입수 방법

**옵션 A. 사내에서 받기 (권장)**
- 삼성화재 내부 디자인팀 / 브랜드팀 문의
- 보통 사내 폰트 라이브러리에 등록되어 있음

**옵션 B. 임시 대체 (개발 단계)**
폰트 파일이 없어도 동작은 합니다. `index.html`의 `@font-face` 선언이 있을 뿐, 실제 본문은 `--f:'Noto Sans KR'`로 렌더링됩니다.

SamsungGL을 명시적으로 사용하는 곳이 없다면 폰트 파일 없이도 사이트는 정상 작동합니다.

## 라이선스 확인사항

배포 전 반드시:
- [ ] Samsung Gothic Long 폰트의 외부 도메인 사용 권한 확인
- [ ] `sfmi.members-center.co.kr` 도메인에서 서빙 가능한지 사내 라이선스 확인
- [ ] 불가능할 경우 Pretendard, Noto Sans KR로 대체 검토

## .gitignore 처리 (라이선스 이슈 시)

폰트 파일 자체를 Git에 올리지 않아야 하는 경우:

```gitignore
# .gitignore
fonts/*.ttf
fonts/*.otf
fonts/*.woff
fonts/*.woff2
!fonts/README.md
```

→ Vercel 환경변수 또는 별도 CDN으로 폰트 제공.
