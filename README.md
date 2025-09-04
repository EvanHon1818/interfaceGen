# Interface Test Case Generator

基于 LangChain 的 API 测试用例自动生成工具。该工具可以根据 API 定义和现有测试用例，自动生成功能测试、性能测试、边界测试和异常测试用例。

## 特性

- 🚀 自动生成多维度测试用例
  - 功能测试：验证 API 的基本功能和业务逻辑
  - 性能测试：检查响应时间、并发处理能力等性能指标
  - 边界测试：测试参数边界值和极限情况
  - 异常测试：验证错误处理和异常情况的响应

- 🧠 智能测试生成
  - 使用大语言模型（LLM）生成测试用例
  - 支持 RAG（检索增强生成）利用现有测试用例
  - 智能提示工程确保生成高质量测试用例

- ⚙️ 灵活配置
  - 支持 OpenAI 和 Azure OpenAI
  - 可配置的模型参数和生成策略
  - 环境变量配置支持

## 项目结构

```
interface_gen/
├── __init__.py          # 项目初始化和公共接口
├── config.py            # 配置管理
├── constants.py         # 常量定义
├── exceptions.py        # 异常类定义
├── core/               # 核心功能
│   ├── generator.py    # 测试用例生成
│   ├── rag.py         # RAG实现
│   └── prompts.py     # 提示模板
├── models/            # 数据模型
│   ├── api.py        # API定义模型
│   └── test_case.py  # 测试用例模型
└── utils/            # 工具类
    ├── json_utils.py # JSON处理
    └── logger.py     # 日志工具
```

## 安装

1. 创建虚拟环境：
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# 或
.venv\Scripts\activate  # Windows
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

## 环境变量配置

创建 `.env` 文件并配置以下环境变量：

### OpenAI 配置
```env
OPENAI_API_KEY=your_api_key
MODEL_NAME=gpt-4-turbo-preview
EMBEDDING_MODEL=text-embedding-3-small
```

### Azure OpenAI 配置（可选）
```env
OPENAI_API_TYPE=azure
OPENAI_API_BASE=your_azure_endpoint
OPENAI_API_VERSION=2024-02-15-preview
AZURE_OPENAI_DEPLOYMENT=your_deployment_name
```

### 其他配置
```env
VECTOR_STORE_PATH=./data/vector_store
TEMPERATURE_FUNCTIONAL=0.7
TEMPERATURE_PERFORMANCE=0.7
TEMPERATURE_BOUNDARY=0.7
TEMPERATURE_EXCEPTION=0.7
```

## 使用方法

1. 准备 API 定义文件（JSON 格式）：

```json
{
  "name": "getUserInfo",
  "description": "获取用户信息接口",
  "method": "GET",
  "path": "/api/users/{userId}",
  "input_params": {
    "userId": {
      "type": "string",
      "description": "用户ID"
    }
  },
  "output_params": {
    "name": {
      "type": "string",
      "description": "用户名"
    },
    "age": {
      "type": "integer",
      "description": "年龄"
    }
  },
  "example_cases": {
    "success_case": {
      "input": {"userId": "12345"},
      "output": {"name": "张三", "age": 25}
    }
  }
}
```

2. 使用命令行工具生成测试用例：

```bash
python -m interface_gen.cli --api-file examples/user_api.json --output test_cases.json
```

可选参数：
- `--test-types`: 指定测试类型（功能/性能/边界/异常）
- `--num-cases`: 每种类型生成的用例数量
- `--debug`: 启用调试模式

## 核心组件

### 1. 配置管理 (`config.py`)
- 统一管理所有配置项
- 支持环境变量配置
- 分离 OpenAI、RAG 和测试配置

### 2. RAG 系统 (`core/rag.py`)
- 使用 FAISS 向量存储
- 支持相似测试用例检索
- 智能利用现有测试用例

### 3. 提示模板 (`core/prompts.py`)
- 针对不同测试类型的专门提示
- 结构化输出格式
- 智能上下文整合

### 4. 测试生成器 (`core/generator.py`)
- 集成 LLM 和 RAG
- 智能测试用例生成
- 结果验证和格式化

### 5. 工具类
- JSON 处理工具
- 日志管理
- 异常处理

## 测试用例类型

### 功能测试
- 验证基本功能
- 检查业务逻辑
- 确保预期输出

### 性能测试
- 响应时间测试
- 并发处理能力
- 资源使用情况

### 边界测试
- 参数边界值
- 数据类型限制
- 特殊字符处理

### 异常测试
- 错误参数处理
- 异常情况响应
- 安全性测试

## 贡献

欢迎提交 Issue 和 Pull Request！

## 许可证

MIT License 