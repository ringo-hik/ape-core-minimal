# APE Core API Documentation

이 문서는 APE Core 시스템의 API 명세와 사용 방법을 설명합니다.

## 목차

1. [LLM Service API](#llm-service-api)
2. [Jira Agent API](#jira-agent-api)
3. [Bitbucket Agent API](#bitbucket-agent-api)
4. [Pocket (S3) Agent API](#pocket-s3-agent-api)
5. [SWDP Agent API](#swdp-agent-api)
6. [Orchestrator API](#orchestrator-api)

## LLM Service API

LLM Service는 다양한 언어 모델(Language Model) API와의 통신을 처리합니다.

### 초기화

```python
from src.core.llm_service import LLMService

# 기본 설정으로 초기화
llm_service = LLMService()
```

### 메서드

#### send_request

LLM에 요청을 보내고 응답을 받습니다.

```python
result = llm_service.send_request(
    messages=[
        {"role": "user", "content": "Hello, how are you?"}
    ],
    model="meta-llama/llama-4-maverick",  # 선택적, 기본값은 DEFAULT_MODEL 환경 변수
    temperature=0.7,                      # 선택적, 기본값 0.7
    max_tokens=2048,                      # 선택적, 기본값 2048
    stream=False,                         # 선택적, 기본값 False
    system_prompt="You are a helpful AI"  # 선택적, 기본값 None
)
```

**매개변수**:
- `messages`: 메시지 객체 리스트, 각 메시지는 role과 content를 포함
- `model`: 사용할 모델 (선택적)
- `temperature`: 응답 생성 온도 (선택적)
- `max_tokens`: 생성할 최대 토큰 수 (선택적)
- `stream`: 응답을 스트리밍할지 여부 (선택적)
- `system_prompt`: 시스템 프롬프트 (선택적)

**반환값**:
```json
{
  "success": true,
  "data": {
    "message": {
      "role": "assistant",
      "content": "I'm doing well, thanks for asking! How can I help you today?"
    },
    "usage": {
      "prompt_tokens": 10,
      "completion_tokens": 15,
      "total_tokens": 25
    },
    "metadata": {}
  }
}
```

#### get_completion

편리한 단일 프롬프트 완성을 위한 간소화된 방법입니다.

```python
result = llm_service.get_completion(
    prompt="What is the capital of France?",
    temperature=0.5  # 추가 매개변수는 send_request와 동일
)
```

**매개변수**:
- `prompt`: 텍스트 프롬프트
- 기타 매개변수는 send_request와 동일

**반환값**:
```json
{
  "success": true,
  "data": "The capital of France is Paris."
}
```

#### set_active_model

활성 모델을 설정합니다.

```python
llm_service.set_active_model("claude-3-opus-20240229")
```

#### get_active_model

현재 활성 모델을 가져옵니다.

```python
model = llm_service.get_active_model()
```

#### get_available_models

사용 가능한 모든 모델 목록을 가져옵니다.

```python
models = llm_service.get_available_models()
```

### 사용 예시

```python
from src.core.llm_service import LLMService, MessageRole

# 초기화
llm_service = LLMService()

# 사용 가능한 모델 목록 가져오기
models = llm_service.get_available_models()
print(f"Available models: {models}")

# 메시지 준비
messages = [
    {"role": MessageRole.SYSTEM, "content": "You are a helpful assistant."},
    {"role": MessageRole.USER, "content": "Tell me about Python programming."}
]

# 요청 보내기
result = llm_service.send_request(messages)

# 결과 처리
if result["success"]:
    response = result["data"]["message"]["content"]
    print(f"Response: {response}")
    
    # 토큰 사용량 표시
    if "usage" in result["data"]:
        usage = result["data"]["usage"]
        print(f"Token usage: {usage}")
else:
    print(f"Error: {result.get('error', 'Unknown error')}")
```

## Jira Agent API

Jira Agent는 Jira 이슈 추적 시스템과의 통합을 제공합니다.

### 초기화

```python
from src.agents.jira_agent import JiraAgent

# 기본 설정으로 초기화 (.env 파일이나 환경 변수에서 설정 읽음)
jira_agent = JiraAgent()
```

### 요청 형식

Jira Agent는 `process` 메서드를 통해 다양한 작업을 지원합니다. 모든 요청은 다음 형식을 사용합니다:

```python
result = jira_agent.process({
    "action": "ACTION_NAME",
    # 액션별 추가 매개변수
})
```

### 지원하는 작업

#### get_issue

Jira 이슈 상세 정보를 가져옵니다.

```python
result = jira_agent.process({
    "action": "get_issue",
    "issue_key": "SCRUM-123"
})
```

#### create_issue

새로운 Jira 이슈를 생성합니다.

**방법 1**: 개별 필드 제공

```python
result = jira_agent.process({
    "action": "create_issue",
    "summary": "이슈 제목",
    "description": "이슈 설명",
    "issue_type": "Task",  # 또는 "Bug", "Story" 등
    "priority": "Medium",  # 선택적
    "labels": ["label1", "label2"],  # 선택적
    "components": ["component1"]  # 선택적
})
```

**방법 2**: 필드 객체 직접 제공 (더 상세한 제어)

```python
result = jira_agent.process({
    "action": "create_issue",
    "fields": {
        "project": {
            "key": "SCRUM"  # 프로젝트 키
        },
        "summary": "이슈 제목",
        "description": "이슈 설명",
        "issuetype": {
            "id": "10001"  # 또는 "name": "Task"
        },
        "priority": {
            "name": "Medium"
        },
        "labels": ["label1", "label2"],
        "components": [
            {"name": "component1"}
        ]
    }
})
```

#### update_issue

기존 Jira 이슈를 업데이트합니다.

```python
result = jira_agent.process({
    "action": "update_issue",
    "issue_key": "SCRUM-123",
    "fields": {
        "summary": "새 제목",
        "description": "새 설명",
        "assignee": {
            "name": "username"
        }
    }
})
```

#### search_issues

JQL(Jira Query Language)을 사용하여 이슈를 검색합니다.

```python
result = jira_agent.process({
    "action": "search_issues",
    "jql": "project = SCRUM AND status = 'To Do'",
    "max_results": 50,  # 선택적, 기본값 50
    "start_at": 0       # 선택적, 기본값 0
})
```

#### add_comment

이슈에 댓글을 추가합니다.

```python
result = jira_agent.process({
    "action": "add_comment",
    "issue_key": "SCRUM-123",
    "comment": "이슈 댓글 내용"
})
```

#### get_projects

모든 프로젝트 목록을 가져옵니다.

```python
result = jira_agent.process({
    "action": "get_projects"
})
```

#### get_issue_types

사용 가능한 이슈 유형 목록을 가져옵니다.

```python
result = jira_agent.process({
    "action": "get_issue_types"
})
```

### 반환 형식

모든 API 호출은 다음과 같은 형식으로 응답합니다:

**성공 시**:
```json
{
  "success": true,
  "data": { /* 작업별 반환 데이터 */ }
}
```

**실패 시**:
```json
{
  "success": false,
  "error": "오류 메시지"
}
```

### 사용 예시

```python
from src.agents.jira_agent import JiraAgent

# 초기화
jira_agent = JiraAgent()

# 인증 테스트
if jira_agent.authenticate():
    print("Jira 인증 성공")
else:
    print("Jira 인증 실패")

# 새로운 이슈 생성
create_result = jira_agent.process({
    "action": "create_issue",
    "summary": "API 문서 작성",
    "description": "APE Core 시스템의 API 문서 작성 필요",
    "issue_type": "Task"
})

if create_result["success"]:
    issue_key = create_result["data"]["key"]
    print(f"이슈 생성됨: {issue_key}")
    
    # 생성된 이슈에 댓글 추가
    comment_result = jira_agent.process({
        "action": "add_comment",
        "issue_key": issue_key,
        "comment": "문서 작성 시작함"
    })
    
    if comment_result["success"]:
        print("댓글 추가됨")
else:
    print(f"이슈 생성 실패: {create_result.get('error')}")
```

## Bitbucket Agent API

Bitbucket Agent는 Bitbucket 소스 코드 관리 시스템과의 통합을 제공합니다.

### 초기화

```python
from src.agents.bitbucket_agent import BitbucketAgent

# 기본 설정으로 초기화 (.env 파일이나 환경 변수에서 설정 읽음)
bitbucket_agent = BitbucketAgent()
```

### 요청 형식

Bitbucket Agent는 `process` 메서드를 통해 다양한 작업을 지원합니다. 모든 요청은 다음 형식을 사용합니다:

```python
result = bitbucket_agent.process({
    "action": "ACTION_NAME",
    # 액션별 추가 매개변수
})
```

### 지원하는 작업

#### get_repositories

저장소 목록을 가져옵니다.

```python
result = bitbucket_agent.process({
    "action": "get_repositories",
    "project_key": "APE"  # 선택적, 기본값은 환경 변수에서 설정
})
```

#### get_repository

특정 저장소의 상세 정보를 가져옵니다.

```python
result = bitbucket_agent.process({
    "action": "get_repository",
    "repo_slug": "repo-name",
    "project_key": "APE"  # 선택적
})
```

#### get_branches

저장소의 브랜치 목록을 가져옵니다.

```python
result = bitbucket_agent.process({
    "action": "get_branches",
    "repo_slug": "repo-name",
    "project_key": "APE"  # 선택적
})
```

#### get_pull_requests

저장소의 풀 리퀘스트 목록을 가져옵니다.

```python
result = bitbucket_agent.process({
    "action": "get_pull_requests",
    "repo_slug": "repo-name",
    "state": "OPEN",      # 선택적, 기본값 "OPEN", 옵션: "OPEN", "MERGED", "DECLINED", "ALL"
    "project_key": "APE"  # 선택적
})
```

#### get_pull_request

특정 풀 리퀘스트의 상세 정보를 가져옵니다.

```python
result = bitbucket_agent.process({
    "action": "get_pull_request",
    "repo_slug": "repo-name",
    "pull_request_id": "123",
    "project_key": "APE"  # 선택적
})
```

#### create_pull_request

새로운 풀 리퀘스트를 생성합니다.

```python
result = bitbucket_agent.process({
    "action": "create_pull_request",
    "repo_slug": "repo-name",
    "title": "풀 리퀘스트 제목",
    "description": "풀 리퀘스트 설명",
    "source_branch": "feature-branch",
    "destination_branch": "main",  # 선택적, 기본값 "master"
    "project_key": "APE",          # 선택적
    "reviewers": ["user1", "user2"]  # 선택적
})
```

#### get_commits

저장소의 커밋 목록을 가져옵니다.

```python
result = bitbucket_agent.process({
    "action": "get_commits",
    "repo_slug": "repo-name",
    "branch": "main",     # 선택적
    "project_key": "APE"  # 선택적
})
```

#### get_file_content

저장소의 특정 파일 내용을 가져옵니다.

```python
result = bitbucket_agent.process({
    "action": "get_file_content",
    "repo_slug": "repo-name",
    "file_path": "path/to/file.py",
    "ref": "main",        # 선택적, 기본값 "master"
    "project_key": "APE"  # 선택적
})
```

### 반환 형식

모든 API 호출은 다음과 같은 형식으로 응답합니다:

**성공 시**:
```json
{
  "success": true,
  "data": { /* 작업별 반환 데이터 */ }
}
```

**실패 시**:
```json
{
  "success": false,
  "error": "오류 메시지"
}
```

### 사용 예시

```python
from src.agents.bitbucket_agent import BitbucketAgent

# 초기화
bitbucket_agent = BitbucketAgent()

# 인증 테스트
if bitbucket_agent.authenticate():
    print("Bitbucket 인증 성공")
else:
    print("Bitbucket 인증 실패")

# 저장소 목록 가져오기
repos_result = bitbucket_agent.process({
    "action": "get_repositories"
})

if repos_result["success"]:
    repos = repos_result["data"]["values"]
    print(f"저장소 {len(repos)}개 찾음:")
    
    for repo in repos:
        print(f"- {repo['name']} ({repo['slug']})")
        
        # 첫 번째 저장소의 브랜치 가져오기
        if repos:
            branch_result = bitbucket_agent.process({
                "action": "get_branches",
                "repo_slug": repos[0]["slug"]
            })
            
            if branch_result["success"]:
                branches = branch_result["data"]["values"]
                print(f"  브랜치 {len(branches)}개:")
                for branch in branches:
                    print(f"  - {branch['displayId']}")
else:
    print(f"저장소 목록 가져오기 실패: {repos_result.get('error')}")
```

## Pocket (S3) Agent API

Pocket Agent는 S3 호환 객체 스토리지와의 통합을 제공합니다.

### 초기화

```python
from src.agents.pocket_agent import PocketAgent

# 기본 설정으로 초기화 (.env 파일이나 환경 변수에서 설정 읽음)
pocket_agent = PocketAgent()
```

### 요청 형식

Pocket Agent는 `process` 메서드를 통해 다양한 작업을 지원합니다. 모든 요청은 다음 형식을 사용합니다:

```python
result = pocket_agent.process({
    "action": "ACTION_NAME",
    # 액션별 추가 매개변수
})
```

### 지원하는 작업

#### list_buckets

버킷 목록을 가져옵니다.

```python
result = pocket_agent.process({
    "action": "list_buckets"
})
```

#### list_objects

버킷 내 객체 목록을 가져옵니다.

```python
result = pocket_agent.process({
    "action": "list_objects",
    "bucket": "bucket-name",  # 선택적, 기본값은 환경 변수에서 설정
    "prefix": "folder/",      # 선택적, 특정 접두사로 필터링
    "max_keys": 1000          # 선택적, 기본값 1000
})
```

#### get_object

객체를 가져옵니다.

```python
result = pocket_agent.process({
    "action": "get_object",
    "bucket": "bucket-name",  # 선택적
    "key": "path/to/file.txt",
    "version_id": "v1"        # 선택적
})
```

#### put_object

객체를 업로드합니다.

```python
result = pocket_agent.process({
    "action": "put_object",
    "bucket": "bucket-name",  # 선택적
    "key": "path/to/file.txt",
    "data": "파일 내용 또는 바이너리 데이터",
    "metadata": {             # 선택적
        "description": "파일 설명"
    }
})
```

#### delete_object

객체를 삭제합니다.

```python
result = pocket_agent.process({
    "action": "delete_object",
    "bucket": "bucket-name",  # 선택적
    "key": "path/to/file.txt"
})
```

#### create_bucket

새 버킷을 생성합니다.

```python
result = pocket_agent.process({
    "action": "create_bucket",
    "bucket": "new-bucket-name",
    "region": "us-east-1"  # 선택적
})
```

### 반환 형식

모든 API 호출은 다음과 같은 형식으로 응답합니다:

**성공 시**:
```json
{
  "success": true,
  "data": { /* 작업별 반환 데이터 */ }
}
```

**실패 시**:
```json
{
  "success": false,
  "error": "오류 메시지"
}
```

### 사용 예시

```python
from src.agents.pocket_agent import PocketAgent

# 초기화
pocket_agent = PocketAgent()

# 버킷 목록 가져오기
buckets_result = pocket_agent.process({
    "action": "list_buckets"
})

if buckets_result["success"]:
    buckets = buckets_result["data"]
    print(f"버킷 {len(buckets)}개 찾음:")
    
    for bucket in buckets:
        print(f"- {bucket['name']} (생성일: {bucket['creation_date']})")
    
    # 텍스트 파일 업로드
    upload_result = pocket_agent.process({
        "action": "put_object",
        "key": "example/test.txt",
        "data": "이것은 테스트 파일입니다.",
        "metadata": {
            "content-type": "text/plain",
            "description": "테스트 파일"
        }
    })
    
    if upload_result["success"]:
        print("파일 업로드 성공")
        
        # 업로드한 파일 가져오기
        get_result = pocket_agent.process({
            "action": "get_object",
            "key": "example/test.txt"
        })
        
        if get_result["success"]:
            content = get_result["data"]["content"]
            print(f"파일 내용: {content}")
    else:
        print(f"파일 업로드 실패: {upload_result.get('error')}")
else:
    print(f"버킷 목록 가져오기 실패: {buckets_result.get('error')}")
```

## SWDP Agent API

SWDP Agent는 Software Development Platform 데이터베이스와의 통합을 제공합니다.

### 초기화

```python
from src.agents.swdp_agent import SWDPAgent

# 기본 설정으로 초기화 (.env 파일이나 환경 변수에서 설정 읽음)
swdp_agent = SWDPAgent()
```

### 요청 형식

SWDP Agent는 `process` 메서드를 통해 다양한 작업을 지원합니다. 모든 요청은 다음 형식을 사용합니다:

```python
result = swdp_agent.process({
    "action": "ACTION_NAME",
    # 액션별 추가 매개변수
})
```

### 지원하는 작업

#### execute_query

SQL 쿼리를 실행합니다.

```python
result = swdp_agent.process({
    "action": "execute_query",
    "query": "SELECT * FROM SWP_PROJECT_MST WHERE PROJECT_STATUS_CD = 'S_ACTIVE'",
    "params": {  # 선택적, 쿼리 매개변수
        "status": "S_ACTIVE" 
    }
})
```

#### get_table_schema

특정 테이블의 스키마를 가져옵니다.

```python
result = swdp_agent.process({
    "action": "get_table_schema",
    "table": "SWP_PROJECT_MST"
})
```

#### get_full_schema

전체 데이터베이스 스키마를 가져옵니다.

```python
result = swdp_agent.process({
    "action": "get_full_schema"
})
```

#### get_table_data

테이블 데이터를 가져옵니다.

```python
result = swdp_agent.process({
    "action": "get_table_data",
    "table": "SWP_PROJECT_MST",
    "limit": 100,                                # 선택적, 기본값 100
    "offset": 0,                                 # 선택적, 기본값 0
    "where": "PROJECT_STATUS_CD = 'S_ACTIVE'"   # 선택적
})
```

#### find_related_data

관련 데이터를 찾습니다.

```python
result = swdp_agent.process({
    "action": "find_related_data",
    "table": "SWP_PROJECT_MST",
    "column": "PROJECT_ID",
    "value": 123,
    "relationship_depth": 1  # 선택적, 기본값 1
})
```

### 반환 형식

모든 API 호출은 다음과 같은 형식으로 응답합니다:

**성공 시**:
```json
{
  "success": true,
  "data": { /* 작업별 반환 데이터 */ }
}
```

**실패 시**:
```json
{
  "success": false,
  "error": "오류 메시지"
}
```

### 사용 예시

```python
from src.agents.swdp_agent import SWDPAgent

# 초기화
swdp_agent = SWDPAgent()

# 인증 테스트
if swdp_agent.authenticate():
    print("SWDP 데이터베이스 연결 성공")
else:
    print("SWDP 데이터베이스 연결 실패")

# 테이블 스키마 가져오기
schema_result = swdp_agent.process({
    "action": "get_table_schema",
    "table": "SWP_PROJECT_MST"
})

if schema_result["success"]:
    schema = schema_result["data"]
    print(f"테이블 이름: {schema['name']}")
    print("컬럼:")
    
    for column in schema["columns"]:
        print(f"- {column['name']} ({column['type']}): {column['description']}")
    
    # 프로젝트 데이터 가져오기
    data_result = swdp_agent.process({
        "action": "get_table_data",
        "table": "SWP_PROJECT_MST",
        "limit": 5,
        "where": "PROJECT_STATUS_CD = 'S_ACTIVE'"
    })
    
    if data_result["success"]:
        rows = data_result["data"]["rows"]
        print(f"\n프로젝트 {len(rows)}개 찾음:")
        
        for row in rows:
            print(f"- {row['PROJECT_NAME']} (ID: {row['PROJECT_ID']})")
    else:
        print(f"데이터 가져오기 실패: {data_result.get('error')}")
else:
    print(f"스키마 가져오기 실패: {schema_result.get('error')}")
```

## Orchestrator API

Orchestrator는 여러 에이전트를 조정하여 복잡한 워크플로우를 실행하는 기능을 제공합니다.

### 초기화

```python
from src.core.llm_service import LLMService
from src.agents.orchestrator import Orchestrator

# LLM 서비스 초기화
llm_service = LLMService()

# Orchestrator 초기화
orchestrator = Orchestrator(llm_service)
```

### 메서드

#### register_agent

에이전트를 등록합니다.

```python
orchestrator.register_agent("agent_name", agent_instance)
```

**매개변수**:
- `name`: 에이전트 이름
- `agent`: 에이전트 인스턴스

**반환값**: 성공 시 True, 실패 시 False

#### unregister_agent

등록된 에이전트를 제거합니다.

```python
orchestrator.unregister_agent("agent_name")
```

**매개변수**:
- `name`: 제거할 에이전트 이름

**반환값**: 성공 시 True, 실패 시 False

#### get_registered_agents

등록된 모든 에이전트 이름을 가져옵니다.

```python
agents = orchestrator.get_registered_agents()
```

**반환값**: 에이전트 이름 목록

#### execute_agent

특정 에이전트로 요청을 실행합니다.

```python
result = orchestrator.execute_agent("agent_name", request_data)
```

**매개변수**:
- `agent_name`: 에이전트 이름
- `request`: 요청 데이터

**반환값**: 에이전트의 응답

#### register_workflow

워크플로우를 등록합니다.

```python
orchestrator.register_workflow(
    workflow_id="workflow_name",
    workflow_steps=[
        {
            "agent": "agent_name",
            "action": "action_name",
            "parameters": { /* 액션 매개변수 */ },
            "output_key": "result_key",
            "on_failure": "terminate"  # 또는 "continue"
        },
        # 추가 단계...
    ],
    metadata={  # 선택적
        "description": "워크플로우 설명"
    }
)
```

**매개변수**:
- `workflow_id`: 워크플로우 식별자
- `workflow_steps`: 워크플로우 단계 목록
- `metadata`: 워크플로우 메타데이터 (선택적)

**반환값**: 성공 시 True, 실패 시 False

#### execute_workflow

등록된 워크플로우를 실행합니다.

```python
result = orchestrator.execute_workflow(
    workflow_id="workflow_name",
    input_data={  # 선택적
        "param1": "value1"
    },
    context={  # 선택적
        "context_key": "context_value"
    }
)
```

**매개변수**:
- `workflow_id`: 워크플로우 식별자
- `input_data`: 입력 데이터 (선택적)
- `context`: 컨텍스트 데이터 (선택적)

**반환값**:
```json
{
  "success": true,
  "execution_id": "execution-uuid",
  "workflow_id": "workflow_name",
  "results": [
    /* 각 단계의 결과 */
  ],
  "context": {
    /* 최종 컨텍스트 데이터 */
  }
}
```

#### plan_workflow

사용자 쿼리를 기반으로 LLM을 사용하여 워크플로우를 동적으로 계획합니다.

```python
result = orchestrator.plan_workflow(
    query="사용자 쿼리",
    available_agents=["agent1", "agent2"]  # 선택적
)
```

**매개변수**:
- `query`: 사용자 쿼리
- `available_agents`: 사용 가능한 에이전트 목록 (선택적)

**반환값**:
```json
{
  "success": true,
  "data": {
    "workflow_id": "generated-uuid",
    "steps": [
      /* 생성된 워크플로우 단계 */
    ],
    "query": "사용자 쿼리"
  }
}
```

### 사용 예시

```python
from src.core.llm_service import LLMService
from src.agents.jira_agent import JiraAgent
from src.agents.bitbucket_agent import BitbucketAgent
from src.agents.orchestrator import Orchestrator

# 서비스 초기화
llm_service = LLMService()
jira_agent = JiraAgent()
bitbucket_agent = BitbucketAgent()

# Orchestrator 초기화
orchestrator = Orchestrator(llm_service)

# 에이전트 등록
orchestrator.register_agent("jira", jira_agent)
orchestrator.register_agent("bitbucket", bitbucket_agent)

# 워크플로우 정의 (코드 변경에 대한 Jira 이슈 생성)
code_changes_workflow = [
    {
        "agent": "bitbucket",
        "action": "get_file_content",
        "parameters": {
            "repo_slug": "ape-core",
            "file_path": "README.md"
        },
        "output_key": "readme_content"
    },
    {
        "agent": "jira",
        "action": "create_issue",
        "parameters": {
            "summary": "README 업데이트 필요",
            "description": "README 파일 내용 검토 및 업데이트 필요",
            "issue_type": "Task"
        },
        "output_key": "issue"
    }
]

# 워크플로우 등록
orchestrator.register_workflow(
    "code_changes_workflow",
    code_changes_workflow,
    {"description": "코드 변경에 대한 Jira 이슈 생성"}
)

# 워크플로우 실행
result = orchestrator.execute_workflow("code_changes_workflow")

# 결과 처리
if result["success"]:
    issue = result["context"].get("issue", {})
    issue_key = issue.get("key")
    
    if issue_key:
        print(f"이슈가 생성되었습니다: {issue_key}")
    else:
        print("이슈 정보를 찾을 수 없습니다")
    
    # 각 단계의 결과 확인
    for i, step_result in enumerate(result["results"]):
        print(f"단계 {i+1} - 성공: {step_result['success']}")
else:
    print(f"워크플로우 실행 실패: {result.get('error')}")

# 동적 워크플로우 계획
plan_result = orchestrator.plan_workflow(
    "Jira에 새 작업 이슈를 만들고 README.md 파일 내용을 설명에 추가해줘"
)

if plan_result["success"]:
    planned_workflow_id = plan_result["data"]["workflow_id"]
    print(f"워크플로우 계획 성공: {planned_workflow_id}")
    
    # 계획된 워크플로우 실행
    planned_result = orchestrator.execute_workflow(planned_workflow_id)
    
    if planned_result["success"]:
        print("계획된 워크플로우 실행 성공")
    else:
        print(f"계획된 워크플로우 실행 실패: {planned_result.get('error')}")
else:
    print(f"워크플로우 계획 실패: {plan_result.get('error')}")
```

## API 응답 형식 표준

APE Core의 모든 API는 일관된 응답 형식을 사용합니다:

### 성공 응답

```json
{
  "success": true,
  "data": { /* 서비스/작업별 데이터 */ }
}
```

### 오류 응답

```json
{
  "success": false,
  "error": "오류 메시지"
}
```

반환되는 `data` 또는 기타 필드는 각 서비스 및 작업에 따라 다를 수 있지만, 최상위 레벨의 `success` 및 `error` 필드는 항상 일관됩니다.