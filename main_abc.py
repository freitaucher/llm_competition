from langchain_core.messages import SystemMessage, HumanMessage, AIMessage
from langchain_ollama import ChatOllama
from langchain_core.prompts import ChatPromptTemplate
import re


def remove_all_think_tags(text):
    """Useful once you have deepseek_r1 with reasoning"""
    pattern = r'<think>.*?<\/think>'
    return re.sub(pattern, '', text, flags=re.DOTALL)


with open("prompt_a.txt", "r") as file:
    prompt_template_a = file.read()
with open("prompt_b.txt", "r") as file:
    prompt_template_b = file.read()
with open("prompt_c.txt", "r") as file:
    prompt_template_c = file.read()


# system message templates:
system_message_llm_a = SystemMessage(content=prompt_template_a)
system_message_llm_b = SystemMessage(content=prompt_template_b)
system_message_llm_c = SystemMessage(content=prompt_template_c)


human_template = """
Below is the current debate history.
{debate_history}
"""


human_prompt_template = ChatPromptTemplate.from_messages([
    ("system", "{system_message}"),
    ("human", human_template),
])


# Initialize the LLM
llm = ChatOllama(model="llama3.2:latest", temperature=0.7, device_map="auto")
# llm = ChatOllama(model="deepseek-r1:1.5b", temperature=0.7, device_map="auto")
# llm = ChatOllama(model="deepseek-llm:latest", temperature=0.7, device_map="auto")
# llm = ChatOllama(model="gpt-oss:latest", temperature=0.7, device_map="auto")


# 3. Init dialogue history
debate_history = []
max_turns = 100  # Number of dialogue rounds


def do_single_turn(debate_history, system_message_llm_a, system_message_llm_b, llm_a, llm_b):
    debate_history, stop_a = single_node_step("A", debate_history, system_message_llm_a, llm_a)
    debate_history, stop_b = single_node_step("B", debate_history, system_message_llm_b, llm_b)

    global_stop = False
    if stop_a and stop_b:
        global_stop = True

    return debate_history, global_stop


def single_node_step(name, debate_history, system_message, llm):
    print("-----------------------------------------------------------------------")
    print("\n["+name+"'s Turn]")
    # prompt for А/B: its system message + debate history
    if debate_history == []:
        debate_history = ["Debates start."]
    prompt_for_node = human_prompt_template.format_messages(
        system_message=system_message.content,
        debate_history=debate_history[:]  # "\n".join(debate_history[-4:])
    )
    response = llm.invoke(prompt_for_node)
    response_filtered = remove_all_think_tags(response.content)
    debate_history.append(response_filtered)
    print(f"A: {response_filtered}")
    stop = False
    if "CALL FOR JUDGMENT" in response_filtered or not "COMMAND" in response_filtered:
        stop = True

    return debate_history, stop


# 4. Start dialogue
turn = 0
global_stop = False
while not global_stop:
    print(f"\n\n--- Round {turn+1} ---")
    debate_history, global_stop = do_single_turn(debate_history, system_message_llm_a, system_message_llm_b, llm_a=llm, llm_b=llm)
    turn += 1


########### Judging #################

print(f"\n\n--- Verdict ---")
# Turn C
print("-----------------------------------------------------------------------")
print("\n[C's Turn]")
# making prompt for C: his system_message + history:
prompt_for_c = human_prompt_template.format_messages(
    system_message=system_message_llm_c.content,
    debate_history=debate_history[:]  # "\n".join(debate_history[-4:])
)

response_c = llm.invoke(prompt_for_c)
response_c_filtered = remove_all_think_tags(response_c.content)
debate_history.append(response_c_filtered)
print(f"C: {response_c_filtered}")
