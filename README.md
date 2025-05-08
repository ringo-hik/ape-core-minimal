# APE Core

Agentic Pipeline Engine (APE) Core는 다양한 서비스 통합과 오케스트레이션 기능을 제공하는 시스템입니다.

## Overview

APE Core는 다음 핵심 기능을 중심으로 구성되어 있습니다:

1. LLM 통합 - 다양한 언어 모델 API 연동 (OpenRouter, Anthropic 등)
2. 외부 서비스 통합:
   - Jira: 이슈 추적 및 프로젝트 관리
   - S3/Pocket: 객체 스토리지
   - SWDP: SQL 기반 소프트웨어 개발 플랫폼
   - Bitbucket: 소스 코드 관리
3. 오케스트레이션 기능 - 다중 에이전트 조정 및 워크플로우 관리

## Setup Guide

### Prerequisites

- Python 3.8 이상
- OpenRouter 또는 선호하는 LLM 제공업체의 유효한 API 키
- 외부 API 또는 내부망 API 접근 권한

### Installation

1. 저장소 복제
2. 환경 변수 설정 (Configuration 섹션 참조)
3. 필요한 패키지 설치:

```bash
# 가상환경 생성 및 활성화 (권장)
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 또는
venv\Scripts\activate  # Windows

# 패키지 설치
pip install -r requirements.txt
```

### Path Configuration

APE Core의 모든 경로는 프로젝트 디렉토리를 기준으로 동적으로 계산되어 하드코딩된 절대 경로를 피합니다. 시스템은 다음과 같은 방식으로 경로 독립성을 유지합니다:

```python
# 경로 계산 예시
import os
base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
default_schema_path = os.path.join(base_dir, "schemas", "swdp-db.json")
```

이 접근 방식은 시스템이 어떤 디렉토리 구조에서도 하드코딩된 경로 없이 실행될 수 있도록 합니다.

### Testing

APE Core는 다양한 통합 테스트를 제공합니다:

```bash
# LLM 서비스 테스트
python test_llm.py

# Jira 에이전트 테스트
python test_jira.py

# Jira-LLM 통합 테스트
python test_jira_llm_integration.py
```

## Features

### LLM Service

LLM 서비스는 다양한 LLM 제공업체와의 통신을 지원합니다:

- 환경 변수를 통한 정적 LLM 구성
- `DEFAULT_MODEL` 설정을 통한 다양한 모델 지원 (Llama4, Claude, GPT 등)
- 선택한 모델에 따른 자동 헤더 처리
- 다양한 API 형식에 대한 응답 처리
- API 연결이 불가능한 경우 테스트를 위한 모의(mock) 응답 제공
- 연결 오류 시 자동 복구 및 대체 응답 메커니즘

### Agent System

에이전트 시스템은 다양한 서비스와 통합하기 위한 프레임워크를 제공합니다:

- 기본 에이전트 인터페이스 (BaseAgent)
- 데이터베이스 에이전트 지원 (DBAgent)
- 서비스 에이전트 지원 (ServiceAgent)
- 확장 가능한 플러그인 기반 아키텍처

### Integrations

APE Core는 다음과 같은 통합 기능을 제공합니다:

- **Jira**: 이슈 생성, 조회, 업데이트 및 검색 기능 지원
  - API 토큰 인증
  - 이슈 유형 ID 기반 생성
  - JQL 기반 검색
  - 프로젝트 관리 및 코멘트 추가

- **Pocket (S3)**: 객체 스토리지 지원
  - 파일 업로드/다운로드
  - 버킷 관리
  - 객체 메타데이터 처리

- **SWDP**: SQL 기반 소프트웨어 개발 플랫폼
  - SQL 쿼리 실행
  - 스키마 탐색
  - 데이터 검색 및 관계 탐색
  - 안전한 쿼리 처리

- **Bitbucket**: 소스 코드 관리
  - 저장소 접근
  - 코드 검색
  - PR 관리
  - 커밋 조회

### Orchestration

오케스트레이션 시스템은 복잡한 작업을 수행하기 위해 여러 에이전트를 조정할 수 있습니다:

- 워크플로우 정의 및 등록
- 컨텍스트 전달을 통한 워크플로우 실행
- LLM을 사용한 동적 워크플로우 계획
- 조건부 실행 및 오류 처리
- 워크플로우 저장 및 관리

## Configuration

APE Core의 구성은 환경 변수 또는 `.env` 파일을 통해 이루어집니다. 프로젝트 루트에 다음 형식으로 `.env` 파일을 생성하세요:

```
# LLM 서비스 구성
APE_LLM_ENDPOINT=https://openrouter.ai/api/v1/chat/completions
DEFAULT_MODEL=meta-llama/llama-4-maverick
APE_OPENROUTER_API_KEY=your-openrouter-key
APE_ANTHROPIC_API_KEY=your-anthropic-key

# Jira 통합
APE_JIRA_URL=https://your-jira-instance.atlassian.net
APE_JIRA_API_TOKEN=your-jira-api-token
APE_JIRA_USERNAME=your-email@example.com
APE_JIRA_PROJECT_KEY=YOUR-PROJECT

# S3/Pocket 통합
APE_POCKET_ENDPOINT=https://your-s3-endpoint.example.com
APE_POCKET_ACCESS_KEY=your-access-key
APE_POCKET_SECRET_KEY=your-secret-key
APE_POCKET_REGION=your-region
APE_POCKET_DEFAULT_BUCKET=your-bucket

# SWDP 데이터베이스
APE_SWDP_DB_HOST=your-db-host.example.com
APE_SWDP_DB_PORT=3306
APE_SWDP_DB_USER=db-user
APE_SWDP_DB_PASSWORD=db-password
APE_SWDP_DB_NAME=db-name

# Bitbucket 통합
APE_BITBUCKET_URL=https://api.bitbucket.org/2.0
APE_BITBUCKET_API_TOKEN=your-bitbucket-token
APE_BITBUCKET_USERNAME=your-email@example.com
APE_BITBUCKET_WORKSPACE=your-workspace
APE_BITBUCKET_PROJECT_KEY=YOUR-PROJECT
```

개발 환경에서는 시스템이 모든 구성 설정에 대한 대체값을 포함하지만, 프로덕션 환경에서는 모든 필수 값을 적절히 구성해야 합니다.

### 내부망 vs 외부망 API 구성

이 시스템은 프로덕션 환경에서 내부 API에 연결하도록 설계되었습니다. 개발 및 테스트를 위해 적절한 구성으로 외부 API에 연결할 수 있습니다.

- **프로덕션 환경**: 적절한 인증이 포함된 내부 API 엔드포인트 사용
- **개발 환경**: API 키를 사용한 외부 API 엔드포인트(OpenRouter 등) 사용

### 확장 및 멀티 에이전트 통합

APE Core를 효과적으로 활용하기 위한 확장 가이드:

1. 새로운 에이전트 개발:
   - `BaseAgent`, `DBAgent` 또는 `ServiceAgent` 클래스 상속
   - 필수 메서드 구현 (`process`, `get_capabilities`, `validate_request` 등)
   - `.env` 파일에 필요한 환경 변수 추가

2. 워크플로우 설계:
   - 오케스트레이터를 사용하여 여러 에이전트 등록
   - 단계별 워크플로우 정의
   - 컨텍스트 공유 및 출력 파라미터 사용

3. LLM-에이전트 통합:
   - LLM 기반 의사 결정을 위한 분석 워크플로우 구성
   - 에이전트 결과 기반 LLM 프롬프트 생성
   - LLM 응답을 에이전트 파라미터로 사용

## Directory Structure

```
ape-core/
├── schemas/             # 서비스용 JSON 스키마
├── src/
│   ├── core/            # 핵심 기능
│   │   ├── agent_interface.py
│   │   ├── llm_service.py
│   │   └── ...
│   ├── agents/          # 에이전트 구현
│   │   ├── jira_agent.py
│   │   ├── pocket_agent.py
│   │   ├── swdp_agent.py
│   │   ├── bitbucket_agent.py
│   │   └── orchestrator.py
│   └── utils/           # 유틸리티 함수
│       ├── db_utils.py
│       ├── response_utils.py
│       └── ...
├── .env                 # 환경 구성
├── test_llm.py          # LLM 서비스 테스트
├── test_jira.py         # Jira 에이전트 테스트
├── test_jira_llm_integration.py # 통합 테스트
└── README.md            # 문서
```

## Usage Examples

### LLM Service 사용

```python
from src.core.llm_service import LLMService

# LLM 서비스 초기화
llm_service = LLMService()

# 요청 보내기
result = llm_service.send_request([
    {"role": "user", "content": "Hello, how are you?"}
])

if result["success"]:
    print(result["data"]["message"]["content"])
```

### Jira Agent 사용

```python
from src.agents.jira_agent import JiraAgent

# Jira 에이전트 초기화
jira_agent = JiraAgent()

# 이슈 생성 - 방법 1: 이슈 유형 이름 사용
result = jira_agent.process({
    "action": "create_issue",
    "summary": "테스트 이슈",
    "description": "이슈 설명",
    "issue_type": "작업"
})

# 이슈 생성 - 방법 2: 이슈 유형 ID 사용 (더 안정적)
result = jira_agent.process({
    "action": "create_issue",
    "fields": {
        "project": {
            "key": "SCRUM"
        },
        "summary": "테스트 이슈",
        "description": "이슈 설명",
        "issuetype": {
            "id": "10001"  # 작업 이슈 유형 ID
        }
    }
})

if result["success"]:
    print(f"이슈 생성됨: {result['data']['key']}")
```

### 오케스트레이션 사용

```python
from src.core.llm_service import LLMService
from src.agents.jira_agent import JiraAgent
from src.agents.orchestrator import Orchestrator

# 서비스 초기화
llm_service = LLMService()
jira_agent = JiraAgent()

# 오케스트레이터 초기화
orchestrator = Orchestrator(llm_service)
orchestrator.register_agent("jira", jira_agent)

# 워크플로우 정의
workflow_steps = [
    {
        "agent": "jira",
        "action": "get_issue",
        "parameters": {"issue_key": "SCRUM-1"},
        "output_key": "issue"
    },
    {
        "agent": "jira",
        "action": "add_comment",
        "parameters": {
            "issue_key": "${issue.key}",
            "comment": "이 이슈가 처리되었습니다."
        }
    }
]

# 워크플로우 등록
orchestrator.register_workflow("process_issue", workflow_steps)

# 워크플로우 실행
result = orchestrator.execute_workflow("process_issue")
```

### LLM + Jira 통합 사용

```python
from src.core.llm_service import LLMService
from src.agents.jira_agent import JiraAgent
from src.agents.orchestrator import Orchestrator

# 서비스 초기화
llm_service = LLMService()
jira_agent = JiraAgent()
orchestrator = Orchestrator(llm_service)
orchestrator.register_agent("jira", jira_agent)

# LLM을 사용하여 이슈 설명 생성
prompt = "소프트웨어 인증 오류에 대한 간결한 버그 설명을 작성해 주세요."
llm_result = llm_service.get_completion(prompt)

if llm_result["success"]:
    bug_description = llm_result["data"]
    
    # LLM이 생성한 설명으로 Jira 이슈 생성
    create_workflow = [
        {
            "agent": "jira",
            "action": "create_issue",
            "parameters": {
                "fields": {
                    "project": {"key": "SCRUM"},
                    "summary": "인증 버그: LLM이 생성한 이슈",
                    "description": bug_description,
                    "issuetype": {"id": "10002"}  # 버그 유형
                }
            },
            "output_key": "issue"
        }
    ]
    
    # 워크플로우 등록 및 실행
    orchestrator.register_workflow("create_bug", create_workflow)
    result = orchestrator.execute_workflow("create_bug")
    
    if result["success"]:
        issue_key = result["context"]["issue"]["key"]
        print(f"LLM 기반 이슈 생성됨: {issue_key}")
```

## LLM 및 에이전트 통합 테스트

APE Core는 다양한 테스트 스크립트를 제공합니다:

### LLM 서비스 테스트

```bash
python test_llm.py
```

이 스크립트는 구성된 LLM API에 연결을 시도합니다. API 키가 유효하지 않거나 API를 사용할 수 없는 경우, 시스템은 개발 목적으로 모의 응답으로 전환됩니다.

### Jira 에이전트 테스트

```bash
python test_jira.py
```

Jira API 연동을 테스트하고 이슈 생성, 조회, 댓글 추가 등 기능을 확인합니다.

### LLM-Jira 통합 테스트

```bash
python test_jira_llm_integration.py
```

오케스트레이터를 통해 LLM과 Jira 서비스의 워크플로우 통합 기능을 테스트합니다.

## 문제 해결

일반적인 문제와 해결 방법:

1. **API 키 오류**: `.env` 파일에 API 키가 유효하고 올바른 형식인지 확인하세요.
2. **경로 문제**: 시스템이 하드코딩된 경로 대신 동적 경로 계산을 사용하는지 확인하세요.
3. **연결 오류**: 내부 API 액세스의 경우 올바른 네트워크에 있고 적절한 액세스 권한이 있는지 확인하세요.
4. **Jira 인증 오류**: API 토큰이 유효하며 사용자명이 이메일 형식인지 확인하세요.
5. **LLM 응답 형식 오류**: 모델에 따라 응답 형식 처리 방식을 확인하세요.

## 참고 사항

이 시스템은 내부망에서의 배포를 위해 설계되었으며, LLM 서비스 연결성과 주요 통합에 중점을 둔 APE Core 기능의 단순화된 버전입니다. 내부 배포를 위해 모든 서비스가 내부 API 엔드포인트와 적절한 자격 증명으로 구성되었는지 확인하세요.