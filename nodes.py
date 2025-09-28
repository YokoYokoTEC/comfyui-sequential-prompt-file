import os
import yaml
import threading
import logging
import glob
import folder_paths
#──────────────────────────
# comfyui-sequential-prompt
#──────────────────────────
wildcards_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "wildcards"))
wildcard_lock = threading.Lock()
wildcard_dict = {}

def wildcard_normalize(x):
    return x.replace("\\", "/").replace(' ', '-').lower()

def load():
    global wildcard_dict
    wildcard_dict = {}

    with wildcard_lock:
        for root, directories, files in os.walk(wildcards_path, followlinks=True):
            for file in files:
                if file.endswith('.txt'):
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, wildcards_path)
                    key = wildcard_normalize(os.path.splitext(rel_path)[0])

                    try:
                        with open(file_path, 'r', encoding="ISO-8859-1") as f:
                            lines = f.read().splitlines()
                            wildcard_dict[key] = [x for x in lines if not x.strip().startswith('#')]
                    except yaml.reader.ReaderError:
                        with open(file_path, 'r', encoding="UTF-8", errors="ignore") as f:
                            lines = f.read().splitlines()
                            wildcard_dict[key] = [x for x in lines if not x.strip().startswith('#')]
        #──────────────────────────
        logging.info("[YokoYoko Tec.] Wildcards loading done.")

def get_wildcard_dict():
    global wildcard_dict
    with wildcard_lock:
        return wildcard_dict

def replace(prompt, seed):
    local_wildcard_dict = get_wildcard_dict()
    code                = prompt

    for key in local_wildcard_dict.keys():
        size = int(len(local_wildcard_dict[key]))
        pos  = seed % size
        rep  = "_"+key+"_"
        logging.info(print("[YokoYoko Tec.] %s, %d, %s"%(rep, seed, local_wildcard_dict[key][pos])))
        code = code.replace(rep, local_wildcard_dict[key][pos])

    return code

class SequentialPromptFile:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "prompt": ("STRING",{"multiline": True, "dynamicPrompts": False}),
                "code": ("STRING",{"multiline": False, "dynamicPrompts": False}),
                "batchCount": ("INT",{"default":1, "min":1}),
                "findFile": ("STRING",{"multiline": False,"default":"*.png"}),
                "fileCount": ("INT",{"default":0}),
                "start": ("INT",{"default":0}),
                "seed": ("INT",{"default":0, "min":0})
            },
        }

    RETURN_TYPES = ("STRING",)
    FUNCTION = "go"
    CATEGORY = "YokoYoko.Tec"

    def go(self, prompt, code, batchCount, findFile, fileCount, start, seed):
        path = folder_paths.get_output_directory() + "/" + findFile
        item = glob.glob(path)      # 出力フォルダのファイル数
        cnt = len(item)
        # ──────────────────────────
        logging.info(print("[YokoYoko Tec.] %s"%(seed)))
        no = max(cnt - fileCount, 0)
        str = prompt + replace(code, start + int(no / batchCount))
        # ──────────────────────────
        return (str,)

class SequentialPromptFind:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "findFile": ("STRING",{"multiline": False,"default":"*.png"})
            },
        }

    RETURN_TYPES = ("INT",)
    FUNCTION = "go"
    CATEGORY = "YokoYoko.Tec"

    def go(self, findFile):
        path = folder_paths.get_output_directory() + "/" + findFile
        logging.info(print("[YokoYoko Tec.] %s"%(path)))
        item = glob.glob(path)      # 出力フォルダのファイル数
        cnt = int(len(item))
        logging.info(print("[YokoYoko Tec.] %d"%(cnt)))
        # ──────────────────────────
        return (cnt,)



NODE_CLASS_MAPPINGS = {
    "File":SequentialPromptFile,
    "Find":SequentialPromptFind,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "File":"SQPrompt(File)",
    "Find":"SQPromptFind",
}
