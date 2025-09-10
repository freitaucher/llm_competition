# Purpose

There are three LLM models: A, B, C.  A and B argue their viewpoints in a loop; when argumentation is exhausted, C judges.

`prompt_a.txt`, `prompt_b.txt`, `prompt_c.txt` - plain text prompts, introducing the general discussion topic and instructions for A, B, C.
The results are strongly dependent on prompts formulation!

Subfolder `prompts/` contains several sample topics with prompt examples that you can try.


# Prerequisites:

The models invoked here are from ollama; ollama can be installed as shown in  https://ollama.com/download:
```
curl -fsSL https://ollama.com/install.sh | sh
```
this will setup ollama as a service, but you might change it, see  https://github.com/ollama/ollama/blob/main/docs/linux.md

To enable cuda:
```
export OLLAMA_GPU_DRIVER=cuda
```

If ollama is not running as a service, start it manually:
```
ollama serve
```

Pull some models, which prefer, e.g.:
```
ollama pull llama3.2:latest
ollama pull deepseek-r1:7b
```



# Installation:

Make, start and install the python environment:

```
python3.12 -m venv env
source env/bin/activate
pip install -r reqirements.txt
```

# Run the competition:

## 1. Single computer:

   ### start all in one (no networking):
   ```
	python main_abc.py
   ```
   This is the safest case if nothing else works. Take care that the node lifts all models, if you want to use different ones for A, B, C.
   So far there is no extra configuration file for this script.
   
   ### to emulate three nodes, open three terminals and start in each one:
   ```
	python main_a.py # in terminal 1
	python main_b.py # in terminal 2
	python main_c.py # in terminal 3
   ```

   ### you can run all with bash script `run_abc.sh`, once your environment is installed.


## 2. Three real distinct nodes:

   Depending on your role (A,B or C), start
   ```
   python main_a.py # for A
   python main_b.py # for B
   python main_c.py # for C
   ```

# Configuration:

  Each script has its own config in json format:

  config_a.json - for main_a.py:
  ```
    "prompt_path": "prompt_a.txt",     # prompt template path
    "host_b": "0.0.0.0",               # since A communicates to B, it needs B-s ip/port
    "port_b": 9000,		        
    "model_name":"llama3.2:latest",    # selected model (e.g. from "ollama list")
    "temperature": 0.7,                # temperature of the model
    "device_map": "auto"               # auto/cpu/cuda
    "buffer_size": 32768,              # buffer size for tcp exchange
    "pausing": "False"                 # discussion continues after pressing Enter
  ```

  config_b.json - for main_b.py:
  ```
    "prompt_path": "prompt_b.txt",     # prompt template path
    "myport": 9000,                    # as a server B must provide a port for A
    "host_c": "0.0.0.0",               # since B communicates to C, it needs C-s ip/port
    "port_c": 9000,		        
    "model_name":"llama3.2:latest",    # selected model (e.g. from "ollama list")
    "temperature": 0.7,                # temperature of the model
    "device_map": "auto"               # auto/cpu/cuda
    "buffer_size": 32768,              # buffer size for tcp exchange
    "pausing": "False"                 # discussion continues after pressing Enter    
  ```

  config_c.json - for main_c.py:
  ```		
    "prompt_path": "prompt_c.txt",     # prompt template path
    "my_port": 9000,                   # as a server C must provide a port for B
    "model_name":"llama3.2:latest",    # selected model (e.g. from "ollama list")
    "temperature": 0.7,                # temperature of the model
    "device_map": "auto"               # auto/cpu/cuda
  ```
  
In case if you emulate all three nodes on one computer, use the same ip "0.0.0.0" but different ports.