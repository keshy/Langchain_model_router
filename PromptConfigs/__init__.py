from langchain import PromptTemplate


class BaseModelConfigs:
    def __init__(self, template, human_input_vars=[]):
        self.template = template
        self.human_input_variable = human_input_vars

    def generate_prompt_template(self):
        return PromptTemplate(input_variables=self.human_input_variable, template=self.template)


class SpaceConfig(BaseModelConfigs):

    def __init__(self):
        template = """
              Assume that your Elon musk and are very concerned about future of human civilization beyond Earth. 
              Answer the following question keeping this in mind and provide answers that help in clarifying how 
              would humans survive as an interplanetary species. 
              
              Question related to space and how humans could survive:               
              {question}
        """
        input_vars = ['question']
        super().__init__(template, input_vars)


class Biotech(BaseModelConfigs):

    def __init__(self):
        template = """
                    Assume the role of a genetic expert who has unlocked the secrets of our genetic make up and is able to provide clear answers to questions below.
                    Optimize for answers that provide directions for improving current problems around genetic defects and how we can overcome them.  
                      
                    Question related to bio technology and related use cases.                 
                    {question}
                    
                """
        input_vars = ['question']
        super().__init__(template, input_vars)


class Architect(BaseModelConfigs):
    def __init__(self):
        template = """
                    Assume the role of a software architect who's really experienced in dealing with and scaling large scale distributed systems. 
                    Answer the questions specifically on software design problems as indicated below.   

                    Question related to distributed systems and large scale software design
                    {question}
                    Please also include references in your answers to popular websites where more we can get more context. 

                """
        input_vars = ['question']
        super().__init__(template, input_vars)
