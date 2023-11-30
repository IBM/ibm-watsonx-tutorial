PROMPT_BACKGROUND_CONTEXT = """ 
Context: References encompass a compilation of abstracts summarizing the contents of CV curriculum vitae  Files, 
each correlated with the name of candidates. Each file name is association with the candidate's name, 
contact information such as email addresses, mobile numbers, geographical location, skill sets, 
educational qualifications, certifications, educational institutions , schools colleges etc. It may contains candidate's  
number of years or months of experiences. It may have company name where candidates are/were employed, their job titles, 
the duration of their tenure, and responsibilities.Furthermore, it can have the candidate's profile, any accolades or acknowledgments 
they have garnered, achievements, attended training  as well as a  both soft and technical skills. 
"""

WATSONX_PROMPT='You are a helpful assistant.First please read "References:" section below, then answer question based only on those References.' + \
                    'If the question cannot be answered using the references provided, answer with "I don\'t know. Please rephrase your query elaborately."' + \
                    "\n\n References:" + \
                    "<<CONTEXT>>" + \
                    "\n\n" +\
                    "\n\nQuestion:" + \
                    "<<QUESTION>>" +\
                    "\n\nAnswer:\n\n"
