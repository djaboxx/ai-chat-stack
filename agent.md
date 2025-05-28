# High Level goal of Agent
We want an agent that can perform code analysis and generation to be able to solve problems in a code base. This is intended to be a tool that will allow ANYONE to be able to contribute to a coding project just by logging in and pulling an issue and leting this agent process the work.

We'll need carefully considered prompting to get the most performance, we'll also want our agent to be tuned with settings that will make it give both creative and analytic answers.

## Agent
I need a PydanticAI Agent that can add the various github functions in the GitHubService class as tools, will use Gemini. Will be able to integrate with the rest of this project. Will be prompted to be able to plan out and execute codechanges. We want to be able to get an issue from a github repo and use that as our prompt. 

### Example of agent adding tools
```python
import random

from pydantic_ai import Agent, RunContext

agent = Agent(
    'google-gla:gemini-1.5-flash',  
    deps_type=str,  
    system_prompt=(
        "You're a dice game, you should roll the die and see if the number "
        "you get back matches the user's guess. If so, tell them they're a winner. "
        "Use the player's name in the response."
    ),
)


@agent.tool_plain  
def roll_die() -> str:
    """Roll a six-sided die and return the result."""
    return str(random.randint(1, 6))


@agent.tool  
def get_player_name(ctx: RunContext[str]) -> str:
    """Get the player's name."""
    return ctx.deps


dice_result = agent.run_sync('My guess is 4', deps='Anne')  
print(dice_result.output)
#> Congratulations Anne, you guessed correctly! You're a winner!
```

### Required Documentation
https://ai.pydantic.dev/tools/#registering-function-tools-via-decorator
https://ai.pydantic.dev/agents/
https://googleapis.github.io/python-genai/genai.html