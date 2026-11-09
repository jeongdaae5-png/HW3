# Disk Analyzer

지정한 폴더의 파일을 확장자별로 분류하고 파일 수와 용량을 요약하는 Python 명령줄 도구입니다.

## 기능

- `disk_analyzer.py`: 카테고리별 파일 수·용량과 전체 합계를 표시합니다.
- `disk_analyzerD.py`: 위 기능에 더해 큰 파일 5개, 중복 파일, 장기간 미사용 파일을 표시합니다.

## 요구 사항

- Python 3.9 이상
- 외부 패키지 없음

## 설치

```bash
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

macOS/Linux:

```bash
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## 실행

폴더 경로를 생략하면 `Downloads` 폴더를 우선 사용합니다.

```bash
python disk_analyzer.py <폴더-경로> --no-color
python disk_analyzerD.py <폴더-경로> --no-color
```

확장 버전에서 미사용 파일 기준 일수를 바꾸려면 다음처럼 실행합니다.

```bash
python disk_analyzerD.py <폴더-경로> --inactive-days 60 --no-color
```

이 도구는 분석 대상 파일을 수정하거나 삭제하지 않습니다. 접근할 수 없는 파일은 건너뛰고 마지막에 개수를 표시합니다.
