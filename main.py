from openai import OpenAI
from tools.api_key_file import api_key, model_gpt

import json, time, os
from pydantic import BaseModel

from tools.getSystemInfo import full_info_os
from tools.parse_lib import extract_python_code, execute_generated_code
from tools.screen_lib import capture_screenshot
from tools.prog_lib import (
    get_installed_programs,
    initialize_program_database,
    semantic_search,
    find_program,
    uninstall_program,
    run_program,
    install_program
)

from tools.system_prompt import (
    system_msg,
    tools_txt,
    Plan_desc,
    StandartExec_desc,
    prefix_code
)


client = OpenAI(
    api_key=api_key
)

class Plan(BaseModel):
    Title: str
    WhatIDo: list[str]

class StandartExec(BaseModel):
    Title: str
    Code: str
    WhatIDo: str
    Plan: str

initialize_program_database()

completion = client.beta.chat.completions.parse(
    model=model_gpt,
    messages=[
        {"role": "system", "content": system_msg+"\n"+tools_txt+"\n"+StandartExec_desc},
        {
            "role": "user",
            "content": input("Enter command:")
        }
    ],
    response_format=StandartExec,
)

event = completion.choices[0].message.parsed

json_data = {
    "title": event.Title,
    "code": event.Code,
    "what_i_do": event.WhatIDo,
    "plan": event.Plan
}

print(json_data)
print('-------------')
out = execute_generated_code(prefix_code+json_data["code"])
print(out)