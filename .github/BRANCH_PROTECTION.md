# Branch Protection Rule 설정 가이드

CI 통과 없이 PR 머지를 막으려면 GitHub 저장소에서 아래 설정을 한 번만 해주면 됩니다.

---

## 설정 방법

1. GitHub 저장소 → **Settings** → **Branches** 이동
2. **"Add branch protection rule"** 클릭
3. **Branch name pattern**: `main` 입력

### 필수 체크 항목

| 옵션 | 설정값 | 설명 |
|------|--------|------|
| **Require a pull request before merging** | ✅ ON | main에 직접 push 금지 |
| └ Require approvals | `1` | 관리자 1명 승인 필수 |
| └ Dismiss stale reviews when new commits are pushed | ✅ ON | 새 커밋 시 기존 승인 무효화 |
| └ Require review from Code Owners | ✅ ON | CODEOWNERS에 지정된 사람 승인 필수 |
| **Require status checks to pass before merging** | ✅ ON | CI 통과 필수 |
| └ Require branches to be up to date before merging | ✅ ON | |
| └ **Status checks** (검색해서 추가) | `test` | `test.yml`의 job 이름 |
| └ **Status checks** (검색해서 추가) | `validate` | `validate-pr.yml`의 job 이름 |
| **Do not allow bypassing the above settings** | ✅ ON | 관리자도 예외 없음 |

4. **Save changes** 클릭

---

## 주의사항

- **Status checks** 항목은 해당 workflow가 최소 한 번 실행된 뒤 검색창에 나타납니다.
  첫 번째 PR을 올린 후 설정하세요.
- CODEOWNERS가 동작하려면 저장소가 **public**이거나 **GitHub Team/Enterprise** 플랜이어야 합니다.
- `@jiho` 를 실제 GitHub 사용자명으로 변경하려면 `.github/CODEOWNERS` 파일을 수정하세요.

---

## 설정 후 동작

컨트리뷰터가 PR을 올리면:

```
PR opened
   │
   ├── test.yml        → pytest 56개 테스트 실행
   └── validate-pr.yml → YAML 스키마 검증

모두 ✅ 통과 + @jiho 승인
   │
   └── Merge 허용
```

CI 실패 시 "Review" 버튼이 비활성화되어 검토 요청 자체가 불가합니다.
