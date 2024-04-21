from search_functions import *
from gpt_functions import *
from document_functions  import *

# Generate topics and search queries for each topic
def generate_queries(course_details, number_of_topics=5,model ='gpt-4-turbo-preview'):
    prompt = f""" You are a capable and experienced researcher and professional educator. Provided are details regarding a course outline for which we need to look for references. 
Figure out the topics that are relevant to this course and generate queries to search for academic resources on Google Scholar.
    - For the arrangement of the topics, make sure the flow is appropriate for the course i.e. beginning with a general topic or overview and then moving on to more specific topics.
For each topic, you'll need to generate a separate query to look for potential academic resources to be used as reference materials for this course.
Generate a total of {number_of_topics} queries for the same number of topics to search in Google Scholar.
Output only the queries in the following json format:
{{
    "queries": [
        {{
            "topic": "topic 1",
            "query": "query 1"
        }},
        {{
            "topic": "topic 2",
            "query": "query 2"
        }}...
    ]
}}

Course Details:
{course_details}
"""
    
    queries = gpt_response(prompt,model,response_format='json_object')
    return queries

# For each query, get the top 3 result from Google Scholar and combine into a single string
def get_search_results(queries_json, num_results = 3):
    """
    Params:
    queries_json (json): The json object containing the queries and topics from generate_queries() function
    """
    total_search_results = ""
    for query in queries_json['queries']:
        results = search_google_scholar(query['query'],num_results)
        temp_result =f"Topic: {query['topic']}\nResults:\n"
        # print(results)
        try:
            for search_results in results['organic_results']:
                temp_result += f"""
                Title: {search_results['title']}
                Link: {search_results['link']}
                Snippet: {search_results['snippet']}
                Publication Summary: {search_results['publication_info']['summary']}"""
        except:
             continue
        total_search_results += temp_result
    
    return total_search_results

# Generate Learning Outcomes
def generate_learning_outcomes(course_details, total_search_results, citation_style='APA', number_of_topics=5,model = 'gpt-4-turbo-preview'):
    """
    Params:
    course_details (str): The course details inputted by user
    total_search_results (str): The search results from search_google_scholar() function
    """
    learning_outcomes_prompt = f'''You are a highly-capable researcher and professional educator. 
    Provided below are course details for a course outline you will need to generate.

Course Details:
    {course_details}

You are tasked to generate the following for a course outline for this course:
    1 Course Learning Outcomes (CLOs)
    2 Topics/ Modules and Intended Learning Outcomes (ILOs)
        - each topic requires at least 2 ILOs
        - each topic should be marked by starting with "Topic #", and each ILO should be marked by starting with "ILO #"
        - add the source/s for each topic
        - there should be {number_of_topics} topics in total
    3 References (at least 1 reference per topic and in {citation_style} format)
        
Provided below are the search results for reference material from Google Scholar for suggested topics to cover in this course. 
You may decide which topics and search results to include in the final result. 
Do not include all search results in the final course outline, and do not add sources not included below.

{total_search_results}
'''

    learning_outcomes = gpt_response(learning_outcomes_prompt,model)
    return learning_outcomes

# Generate Course Outline
def generate_course_outline(course_details, learning_outcomes, number_of_topics=5, total_hours=54, weekly_hours=3,model = 'gpt-4-turbo-preview'):
    activities_prompt_json = f'''You are a highly-capable researcher and professional educator. Provided below are course details for a course outline you will need to generate.

    Course Details:
    {course_details}
    {learning_outcomes}

    -------------------

    From the provided learning outcomes, create weekly activities for the course. 
    This course divided into {number_of_topics} topics with a total of {total_hours} hours for the whole semester divided into {weekly_hours} hours per week ({total_hours//weekly_hours} weeks in total).
    You may stretch one topic over the course of multiple weeks or add topics not included in the learning outcomes
    Each activity should have a week number, topic, activity description, expected output or assessment, and assessment tools.
    Follow the json formatting below:

    {{
        "course_title": The provided course title,
        "course_description": The provided course description,
        "instructor_name": "Instructor Name",
        "credit_units": "Credit Units",
        "total_hours": "Total Hours",
        "weekly_hours": "Weekly Hours",
        "clos": [
            "CLO 1",
            "CLO 2",
            "CLO 3"
        ],
        "topics": [
            {{
                "topic": "Topic 1",
                "ilos": [
                    "ILO 1",
                    "ILO 2"
                ]
            }},
            {{
                "topic": "Topic 2",
                "ilos": [
                    "ILO 1",
                    "ILO 2"
                ]
            }}...
        ],
        "references":[
            {{
                reference: "Reference 1"
                link: "Link 1"
            }}
        ]
        "activities": [
            {{
                "week": "Week 1",
                "topic": "Topic 1",
                "activity_description": "activity description 1",
                "expected_output": "expected output 1",
                "assessment_tools": "assessment tools 1"
            }},
            {{
                "week": "Week 2",
                "topic": "Topic 2",
                "activity_description": "activity description 2",
                "expected_output": "expected output 2",
                "assessment_tools": "assessment tools 2"
            }}...
        ]
    }}

    Avoid modifying any of the provided details especially the course title, course description, and CLOs
    '''
    course_outline_json = gpt_response(activities_prompt_json,model, response_format='json_object')
    return  course_outline_json

# Generate activities
def generate_activities(course_outline_json,model = 'gpt-4-turbo-preview'):
    pass