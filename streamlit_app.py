import streamlit as st
from app_functions import *
import os
import json
import time
import datetime

if "doc_path" not in st.session_state:
    st.session_state.doc_path = None
if 'execution_time' not in st.session_state:
    st.session_state.execution_time = None
if 'output_file_path' not in st.session_state:    
    st.session_state.output_file_path= None
    st.session_state.output_file_name = None
if 'learning_outcomes' not in st.session_state:
    st.session_state.learning_outcomes = None
if 'default_description' not in st.session_state:
    st.session_state.default_description = None
if 'doc_buffer' not in st.session_state:
    st.session_state.doc_buffer = None

# Logo
left_co, cent_co,last_co = st.columns(3)
with cent_co:
    st.image('CurriculumGPT_Logo.png')
# Title
st.markdown("""
    <h1 style='text-align: center;'>CurriculumGPT</h1>
    """, unsafe_allow_html=True)

# Input course details
with st.expander("MAIN INPUTS",True):
    course_title = st.text_input("Course Title", None)
    target_students = st.text_input("Target Students",placeholder="e.g. 3rd year BS Computer Science students",value = None)
    course_description = st.text_area("Course Description", height=200,value = st.session_state.default_description)

    if st.button("*Auto-generate Description*") :
        if course_title and target_students is not None:
            st.session_state.default_description = generate_description(course_title,target_students)
            st.rerun()
        else:
            st.error("*Please input both Course Title and Target Students*")

    instructor_name = st.text_input("Instructor Name",placeholder="e.g. Dr. Juan Dela Cruz")

with st.sidebar:
    st.title('Additional Inputs')

    with st.expander("COURSE CREDIT INPUTS",True):
        credit_units = st.number_input("Credit Units", value=3)
        total_hours = st.number_input("Total Hours", value=54)
        weekly_hours = st.number_input("Weekly Hours", value=3)
    with st.expander("PROCESS INPUTS", True):
        citation_style = st.selectbox("Citation Style", ["APA", "MLA", "Chicago", "Harvard"])
        model = st.selectbox('Choose gpt model',['gpt-4o','gpt-4-turbo','gpt-3.5-turbo'])
        document_title = st.text_input("Output Title",placeholder='Course_Outline.docx')
    st.write("*This app was designed on Streamlit by Jun Albert S. Pardillo (2024).*")

if st.button("GENERATE COURSE OUTLINE",use_container_width=True):
    
    if course_title and course_description is None:
        st.session_state.default_description = generate_description(course_title,target_students)
 
    # Combing the course details into a single string
    course_details = f"""Course Title: {course_title}
    Course Description: {course_description}
    Instructor Name: {instructor_name}
    Credit Units: {credit_units}
    Target Students: {target_students}
    Total Hours: {total_hours}
    Class Hours per Week: {weekly_hours}"""

    st.session_state.start_time = time.time()

    with st.spinner("Generating Search Queries..."):
        # Genereate topics and search queries
        queries =  generate_queries(course_details=course_details)
    st.success("Queries Generated")

    with st.spinner("Searching Online for Reference Materials..."):
        # Get Search Results from Google Scholar
        total_search_results = get_search_results(json.loads(queries))
    st.success("Search Results Generated")

    with st.spinner("Generating Learning Outcomes..."):
        # Get Learning Outcomes from GPT-4
        st.session_state.learning_outcomes = generate_learning_outcomes(
            course_details=course_details, 
            total_search_results=total_search_results, 
            citation_style=citation_style,
            model=model
        )

    if st.session_state.learning_outcomes:
        st.success("Learning Outcomes Generated")
    else:
        st.error("Learning Outcomes failed")
    learning_outcomes = st.session_state.learning_outcomes


    with st.spinner("Generating Course Outline..."):
        # Generate Course Outline
        course_outline = generate_course_outline(
            course_details=course_details, 
            learning_outcomes=learning_outcomes, 
            total_hours=total_hours, 
            weekly_hours=weekly_hours,
            model=model
        ) 
        course_outline_json = json.loads(course_outline)

    # Create word document from course outline json
    st.session_state.doc_buffer = create_word_document_from_json(course_outline_json, title=document_title, streamlit=True)
    
    if document_title == '':
        document_title = f"{course_title.replace(' ','_')}_{instructor_name.replace(' ','_')}_Course_Outline"
    st.session_state.output_file_name = f"{document_title}.docx"
    end_time = time.time()
    st.session_state.execution_time = end_time - st.session_state.start_time
    st.session_state.start_time = None


# Once process is finished, provide output
if st.session_state.output_file_name:
    st.subheader("Learning Outcomes")
    st.write(st.session_state.learning_outcomes)

    # Provide download button/link
    mins = round((st.session_state.execution_time // 60),0)
    secs = round((st.session_state.execution_time % 60),0)
    st.write(f"Execution Time: {int(mins)} minutes and {int(secs)} seconds")
    btn = st.download_button(
        label="Download Course Outline",
        data=st.session_state.doc_buffer,
        file_name=st.session_state.output_file_name,
        mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )
    st.write("Please fulfill this assessment form to rate the output, thank you!")
    st.markdown("[Course Outline Assessment Form](https://forms.gle/2vekf9A6xATSHi2bA)")
