# A repo for testing and demoing features of GitHub Copilot CLI and the SDK

[Burke Holland Demo](https://developer.microsoft.com/blog/bringing-work-context-to-your-code-in-github-copilot)

```bash

# Set your OpenAI Key" (minimal success)
gh secret set OPENAI_API_KEY --app codespaces

export OPENAI_API_KEY="your api key goes here"

copilot

# Sometimes the copy-paste functionality doesn't seem to work here - you may need to re-type these commands from scratch into the CLI

/login

/plugin marketplace add github/copilot-plugins

/plugin install workiq@copilot-plugins 

# Restart the CLI

Prompt: Create a fantasy inspired image of a girl in wonder while lost in a forest with lots of wildlife and lush greenery around.

```