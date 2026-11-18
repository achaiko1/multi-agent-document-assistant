# Multi-Agent Document Intelligence

**An AI-powered document processing system built with Python, LangGraph, LangChain, and Pydantic.**

Multi-Agent Document Intelligence orchestrates specialized AI agents to retrieve information, answer questions, summarize documents, and perform mathematical calculations on financial and healthcare records.

The system uses LLM-based intent classification to dynamically route requests through a LangGraph workflow, with structured output validation, tool execution logging, and multi-turn conversational memory.

## Key Features

- **Multi-Agent Orchestration:** Routes user requests between three specialized AI agents using LangGraph.
- **Intelligent Intent Classification:** Classifies requests as question answering, summarization, or calculation using structured LLM output.
- **Document Retrieval:** Searches and retrieves relevant financial and healthcare documents.
- **Tool-Augmented Reasoning:** Uses dedicated document retrieval and calculator tools to produce grounded responses.
- **Structured Output Validation:** Enforces typed response schemas using Pydantic.
- **Conversational Memory:** Maintains context across multiple interactions and supports restoring saved conversation histories.
- **Safe Arithmetic Evaluation:** Uses Python's Abstract Syntax Tree (AST) to restrict mathematical operations rather than executing arbitrary Python code.
- **Execution Logging:** Records tool invocations and results for debugging and observability.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Core application and backend logic |
| LangGraph | Multi-agent orchestration and state management |
| LangChain | LLM integration, prompt templates, and tools |
| OpenAI GPT-4o | Language understanding and response generation |
| Pydantic | Structured outputs and input validation |
| Python AST | Safe mathematical expression evaluation |
| JSON | Session history and tool execution logging |

## System Architecture

![LangGraph Agent Architecture](docs/langgraph_agent_architecture.png)

The system processes requests through five interconnected LangGraph nodes:

**1. Intent Classification**

The incoming user request is analyzed by an LLM configured to return a validated `UserIntent` object. The classifier identifies the appropriate agent based on the request and conversation context.

**2. Specialized Agent Execution**

Requests are routed to one of three agents:

- **Q&A Agent:** Retrieves relevant documents and answers factual questions with source references.
- **Summarization Agent:** Extracts important information and produces document summaries.
- **Calculation Agent:** Retrieves numerical data and invokes the calculator tool to perform arithmetic.

**3. Memory Update**

After an agent completes its task, the `update_memory` node summarizes the conversation and tracks referenced document IDs.

**4. State Persistence**

LangGraph's `InMemorySaver` maintains conversation state during execution. Session histories are also stored as JSON files, allowing previous user and assistant messages to be reconstructed when a saved session is resumed.

### Workflow

`User Input → Intent Classifier → Specialized Agent → Memory Update → END`

Conditional edges determine which specialized agent executes. The workflow is compiled with a LangGraph checkpointer to support stateful interactions.

## Example Usage

The following examples were tested against the project's sample document collection.

### Document Question Answering

**User:**
> Who is the client in invoice INV-002?

**Assistant:**
> The client in invoice INV-002 is TechStart Inc.

Intent: `qa`

Tools: `document_reader`

### Document Summarization

**User:**
> Summarize contract CON-001.

**Assistant:**
> Contract CON-001 is a 12-month service agreement between DocDacity Solutions Inc. and Healthcare Partners LLC. The agreement includes document processing, technical support, analytics reporting, and compliance monitoring. The contract has a monthly fee of $15,000 and a total value of $180,000.

Intent: `summarization`

Tools: `document_reader`

### Multi-Document Calculation

**User:**
> What is the difference between the total amounts of invoices INV-002 and INV-003?

**Assistant:**
> The difference between the two invoices is $145,200.
>
> INV-002: $69,300
>
> INV-003: $214,500
>
> Calculation: $214,500 − $69,300 = $145,200.

Intent: `calculation`

Tools: `document_reader`, `calculator`

Sources: `INV-002`, `INV-003`

### Context-Aware Follow-Up

**User:**
> Who is the client in invoice INV-002?

**Assistant:**
> The client is TechStart Inc.

**User:**
> What is the total amount due on that invoice?

**Assistant:**
> The total amount due on invoice INV-002 is $69,300.

The assistant resolves the reference to "that invoice" using prior conversation context.

## Getting Started

### Prerequisites

- Python 3.9 or newer, with Python 3.13 used during local development
- An API key compatible with the configured model provider
- Git (optional)

### Installation

Clone the repository:

```bash
git clone https://github.com/achaiko1/multi-agent-document-assistant.git
cd multi-agent-document-assistant
```

Create and activate a virtual environment.

**Windows PowerShell:**

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**macOS/Linux:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

### Environment Configuration

Create a `.env` file based on `.env.example` and configure the API credentials:

```dotenv
OPENAI_API_KEY=your_api_key_here
MODEL_NAME=gpt-4o
TEMPERATURE=0.1
SESSION_STORAGE_PATH=./sessions
```

**Provider note:** The current implementation is configured for the Udacity/Vocareum OpenAI-compatible API endpoint. Running it requires compatible credentials. Using a standard OpenAI API key requires configuring the corresponding API endpoint.

Never commit real API credentials to version control.

### Running the Application

```bash
python main.py
```

The application launches an interactive command-line interface supporting document questions, summaries, calculations, and multi-turn conversations.

Available commands:

- `/help` — Display available commands
- `/docs` — List sample documents
- `/quit` — Exit the application

## Project Structure

```text
multi-agent-document-assistant/
├── docs/
│   └── langgraph_agent_architecture.png
├── src/
│   ├── __init__.py
│   ├── agent.py
│   ├── assistant.py
│   ├── prompts.py
│   ├── retrieval.py
│   ├── schemas.py
│   └── tools.py
├── main.py
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

Runtime-generated `logs/` and `sessions/` directories are excluded from the public repository.

## Engineering Decisions

### Structured LLM Outputs

Pydantic schemas define required response fields and validate model-generated data.

The application uses `with_structured_output()` for intent classification, Q&A, summarization, calculations, and conversation memory updates.

Before storing structured responses in LangGraph state, Pydantic objects are converted into JSON-compatible dictionaries to avoid custom-object deserialization warnings.

### State Management

LangGraph's `AgentState` stores user input, message history, classified intent, routing information, document references, and intermediate responses.

The `messages` field uses the `add_messages` reducer, while `actions_taken` uses `operator.add` to accumulate executed node names.

### Safe Tool Execution

The calculator parses arithmetic expressions using Python's AST module and evaluates only permitted numerical operations.

This prevents unrestricted execution of arbitrary Python expressions and provides error handling for unsupported operations and invalid input.

### Session Management

The application assigns conversation session IDs and stores session histories as JSON files.

LangGraph's `InMemorySaver` supports checkpointed state within a running process. When a previously saved session is resumed after restart, the application reconstructs user and assistant messages from the session JSON file.

This restores conversational context, but does not recreate every historical internal checkpoint or tool execution state.

## Validation and Testing

The application has been manually tested for:

- Correct routing to Q&A, summarization, and calculation agents
- Document lookup and source referencing
- Accurate multi-document calculations
- Calculator invocation and arithmetic correctness
- Rejection of unsafe calculator expressions
- Division-by-zero error handling
- Pydantic validation of invalid confidence scores and intent types
- Automatic JSON tool logging
- Multi-turn conversational context retention
- Restoration of saved conversation messages after application restart

These tests were conducted locally through the command-line application. Automated test coverage and continuous integration are planned enhancements.

## Current Limitations

The current implementation operates on a simulated document collection containing sample invoices, contracts, and insurance claims.

It does not yet provide general-purpose PDF uploads, vector-based semantic retrieval, or a browser-based interface. The current application is primarily an interactive command-line system.

The in-memory LangGraph checkpoints are not durable across application restarts, although saved conversational messages can be reconstructed from JSON session files.

## Planned Enhancements

- User-uploaded PDF and document processing
- Text chunking and semantic retrieval
- Interactive web interface
- Automated unit and integration tests
- GitHub Actions continuous integration
- Deployment of a public demonstration
- Improved error handling and observability

## Project Background

This project originated from a Udacity agentic AI coursework scaffold. The implementation work included completing the agent workflow, intent classification, structured response schemas, prompt selection, calculation tools, memory management, and integration testing.

The repository is being extended into a standalone document-intelligence application, with additional capabilities developed beyond the original coursework.

## License

No license has been selected for this repository. Reuse and distribution permissions for the original coursework materials should be verified before adding an open-source license.
