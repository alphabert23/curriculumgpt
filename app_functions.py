from search_functions import *
from gpt_functions import *
from document_functions  import *

# Generate topics and search queries for each topic
def generate_queries(course_details, model='gpt-4o'):
    prompt = f"""
    You are a capable and experienced researcher and professional educator. Provided are details regarding a course outline for which we need to look for references. 

    Figure out the topics that are relevant to this course and generate queries to search for academic resources on Google Scholar.
    For the arrangement of the topics, make sure the flow is appropriate for the course i.e., beginning with a general topic or overview and then moving on to more specific topics.
    Generate 5 queries and topics to search in Google Scholar. 
    Note that since the purpose of these queries will be to find suitable references tothe course provided, limit the query to only find academic books appropriate for use as references (i.e. textbooks, journals, etc.) 

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
    
    try:
        queries = gpt_response(prompt, model, response_format='json_object')
    except Exception as e:
        print(f"Error generating queries: {e}")
        queries = {"queries": []}
    
    return queries

# For each query, get the top 5 results from Google Scholar and combine into a single string
def get_search_results(queries_json, num_results=5):
    """
    Params:
    queries_json (json): The json object containing the queries and topics from generate_queries() function
    """
    total_search_results = ""
    for query in queries_json.get('queries', []):
        try:
            results = search_google_scholar(query['query'], num_results)
            temp_result = f"Topic: {query['topic']}\nResults:\n"
            
            for search_result in results.get('organic_results', []):
                temp_result += f"""
                Title: {search_result['title']}
                Link: {search_result['link']}
                Snippet: {search_result.get('snippet', 'N/A')}
                Publication Summary: {search_result.get('publication_info', {}).get('summary', 'N/A')}
                """
                
            total_search_results += temp_result
        except Exception as e:
            print(f"Error fetching results for query '{query['query']}': {e}")
            continue
    
    return total_search_results

# Generate Learning Outcomes following Bloom's Taxonomy
def generate_learning_outcomes(course_details, total_search_results, citation_style='APA', model='gpt-3.5-turbo'):
    """
    Params:
    course_details (str): The course details inputted by user
    total_search_results (str): The search results from search_google_scholar() function
    """

    relevant_references_prompt = f""" Provided below are the search results for reference material from Google Scholar for suggested topics for the provided course. Filter out sources that aren't ideal to use as reference material for this course, instead only keep recent and relevant academic materials such as textbooks. Follow the following format for your output:
    
    Title: "Reference Title"
    Link: "Reference Link"
    Snippet: "Reference Snippet"
    Publication Summary: "Reference Publication Summary"

    Course Details:
    {course_details}

    Search Results:
    {total_search_results}"""

    filtered_search_results = gpt_response(relevant_references_prompt,model)

    learning_outcomes_prompt = f'''You are a curricular development expert focused on authoring course outlines.
    Provided below are course details for a course outline you will need to generate.

Course Details:
    {course_details}

You are tasked to generate the following for a course outline for this course:
    1 Course Learning Outcomes (CLOs)
        - CLOs are what students are expected to be able to do by the end of this course
        - Keep them clear but concise
    2 Topics/ Modules and Intended Learning Outcomes (ILOs)
        - ILOs are what students expected to be able to do by the end of this topic
        - each topic should have at least 2 ILOs
        - each topic should be marked by starting with "Topic #", and each ILO should be marked by starting with "ILO #"
    3 References (at least 1 reference per topic and in {citation_style} format)
        - Make sure to include the link (if any) is available
        - Only keep reference that are the most relevant for this course and topic.

Incorporate the concepts of Bloom's Taxonomy in designing the course, making sure to use an appropriate number of Conceptual and Project Learning Outcomes. Conceptual LOs are focused on the first two levels of Bloom's Taxonomy (i.e. Remember and Understand) while Project LOs are focused on higher-order skills (i.e. Create, Evaluate, Analyze, Understand). Depending on the target students, adjust the CLOs and ILOs according to their skill level. For example, an introductory course would have more Conceptual LOs to allow students to build foundational knowledge, while an advanced course would have more Project LOs to allow them to improve upon and apply their existing knowledge. 

Here are some examples of good LOs for different programs:

Arts, Media, and Design
    Discriminate among different Western music styles.
    Discuss how the historical and cultural events contextualize the creation of an artwork.

Business
    Compare and contrast different types of business ownership.
    Evaluate and classify various marketing strategies.

Computer and Information Sciences
    Describe the scientific method and provide an example of its application.
    Develop solutions for security, balancing technical and privacy issues as well as business concerns.

Engineering
    Prepare engineering documents that coherently present information for technical and non-technical audiences.
    Compile and summarize current bioengineering research to discuss the social, environmental, and legal impacts.

Health Sciences
    Describe how nutrition and life style choices impact the life cycle.
    Assess gross muscle strength of upper and lower extremities when assisting a patient in ambulation.

Science
    Distinguish between healthy and unhealthy physical, mental, and emotional patterns.
    Calculate germination rates of various seeds.
    Describe and apply research methods to study child psychology.
    Select appropriate mathematical routines to solve problems.
    Create and interpret molecular models and/or chemical computations.

Social Sciences and Humanities
    Outline the structure of the Constitution of the United States.
    Formulate a stance on a political issue and support the position.

Provided below are the search results for reference material from Google Scholar for suggested topics to cover in this course. Do not add sources not included below.

{filtered_search_results}


'''

    learning_outcomes = gpt_response(learning_outcomes_prompt, model)
    return learning_outcomes

# Generate Course Outline and Activities
def generate_course_outline(course_details, learning_outcomes, total_hours=54, weekly_hours=3,model = 'gpt-3.5-turbo'):
    activities_prompt = f'''You are a highly-capable researcher and curricular development expert. Provided below are course details for a course outline you will need to generate.

    Course Details:
    {course_details}
    {learning_outcomes}

    -------------------

    From the provided learning outcomes, create weekly activities for the course. 
    This course is divided into a total of {total_hours} hours for the whole semester divided into {weekly_hours} hours per week ({total_hours//weekly_hours} weeks in total).

    You may stretch one topic over the course of multiple weeks or add topics not included in the learning outcomes
    Each activity should have a week number, topic, activity description, expected output or assessment, and assessment tools.

    You may make slight modifications to the provided course description for improvements without removing any context, but avoid changing the course title, instructor name, and weekly hours. 
    '''

    # Initial prompt output to generate course outline with text model
    course_outline = gpt_response(activities_prompt,model, response_format='text')

    # print(course_outline)

    # Convert initial output to JSON format
    json_prompt = f"""Convert the provided course outline details into JSON format.

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
                link: "Link 1" // if no link is available, just don't include
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
    
    Course Details:
    {course_details}
    {learning_outcomes}

    Course Outline:
    {course_outline}
    """

    course_outline_json = gpt_response(json_prompt,model, response_format='json_object')

    return  course_outline_json

# Generate course description
def generate_description(course_title,target_students, model = 'gpt-3.5-turbo'):
    description_prompt = f"""You are a highly-capable educator and curricular development expert. Create a comprehensive but concise description for a course called "{course_title}" which is meant for {target_students}. 
    Keep the description within 100 words, and provide a general overview of what one  can expect from this course."""

    description = gpt_response(description_prompt,model)

    return description