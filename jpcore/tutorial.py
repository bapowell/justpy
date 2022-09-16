'''
Created on 2022-09-16

@author: wf
'''
import os
import re
from jpcore.utilities import find_files

class TutorialManager:
    """
    justpy tutorial
    """
    
    def __init__(self,docs_dir:str=None):
        """
        constructor
        
        Args:
            docs_dir(str): the path from which to read the tutorial files
        """
        self.tutorials={}
        self.script_dir = os.path.dirname(__file__)
        if docs_dir is None:
            docs_dir = f"{os.path.dirname(self.script_dir)}/docs"
        self.docs_dir=docs_dir
        self.total_lines=0
        self.total_examples=0
        self.examples_by_name={}
        self.tutorial_files = find_files(self.docs_dir, ".md")
        for tutorial_file_path in self.tutorial_files:
            tutorial=Tutorial(docs_dir,tutorial_file_path)
            self.tutorials[tutorial.name]=tutorial
            self.total_lines+=len(tutorial.lines)
            self.total_examples+=len(tutorial.examples)
            for example in tutorial.examples.values():
                if example.name in self.examples_by_name:
                    duplicate_example=self.examples_by_name[example.name]
                    raise Exception(f"duplicate example name '{example.name}' {example.tutorial.name} and {duplicate_example.tutorial.name}")
                self.examples_by_name[example.name]=example
        
class Tutorial:
    """
    a single tutorial file
    """
    
    def __init__(self,docs_dir,path:str):
        """
        construct me
        """
        self.examples={}
        self.path=path
        self.name=path.replace(docs_dir+"/","")
        self.github_url=f"https://github.com/justpy-org/justpy/blob/master/docs/{self.name}"
        with open(self.path, "r") as markup_file:
            self.markup = markup_file.read()
        self.lines=self.markup.split("\n")
        header=None
        python_code=[]
        in_python_code=False
        for line in self.lines:
            if line.startswith("```python"):
                in_python_code=True
                continue
            if line.startswith("```"):
                in_python_code=False
                continue
            if not in_python_code:
                header_match= re.search("^#+\s*(.*)",line)
                if header_match:
                    header=header_match.group(1)
                    header=header.strip()
                    pass
            else:
                python_code.append(line)
                justpy_match = re.search(
                    """^(jp[.])?justpy[(]([a-zA-Z_0-9]*)([,]\s*(.*))?[)]([#].*)?""", line
                )
                if justpy_match:
                    example_name = justpy_match.group(2)
                    example_option=justpy_match.group(4)
                    example_comment=justpy_match.group(5)
                    if not example_name:
                        example_name=example_comment
                        pass
                    example=Example(self,name=example_name,option=example_option,header=header,lines=python_code)
                    self.examples[example.name]=example
                    header=None
                    python_code=[]
                    in_python_code=False

class Example:
    """
    an example
    """
    
    def __init__(self,tutorial:Tutorial,name:str,option:str=None,header:str="",lines:list=[]):
        """
        constructor
        
        Args:
            tutorial(Tutorial): the tutorial that i am part of
            name(str): the name of the example
            option(str): option
            header(str): the header/description of the example
            lines(list): the source code lines
        """
        self.tutorial=tutorial
        self.name=name
        self.option=option
        self.header=header
        self.lines=lines
        self.github_url=None
        if self.header is not None:
            # https://stackoverflow.com/questions/72536973/how-are-github-markdown-anchor-links-constructed
            lower=self.header.strip().lower().replace(" ","-")
            anchor=""
            for c in lower:
                if c.isalnum() or c in "-_":
                    anchor+=c
            self.github_url=f"{self.tutorial.github_url}#{anchor}"
        