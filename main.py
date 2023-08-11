import openai
import streamlit as st
import pandas as pd

from Secret_key import openai_key


def get_options() -> dict:
    # gets the options for the select boxes
    options = {"Topic": ["JavaScript"], "SubTopic": ["Basic Concepts", "DOM", "Advanced Concepts"],
               "Subtopic-concept_dictionary": {
                   "Basic Concepts": ["Data Types and Variables", "Operators", "Conditionals", "Loops", "Functions",
                                      "Strings",
                                      "Objects and Classes", "Arrays"],
                   "DOM": ["Selecting Elements", "Modifying Elements", "Creating and Deleting Elements", "Events"],
                   "Advanced Concepts": ["Asynchronous Javascript", "Callbacks", "Promises", "Fetch API", "Async Await",
                                         "Error Handling"]
               }, "Blooms": ["Creating", "Remembering", "Applying"], "learning_outcome": {}}

    path = r"https://github.com/Ishita-Khatri/JavaScriptTutor/blob/main/AI%20assignment%20metadata%20for%20Javascript%20-%20Learning%20Outcomes.csv"
    df = pd.read_csv(path, encoding='utf-8')
    for index, row in df.iterrows():
        concept = row['concept']
        blooms_level = row["blooms_level"]
        outcome = row['learning_outcome']

        if concept not in options["learning_outcome"]:
            options["learning_outcome"][concept] = {}

        if blooms_level not in options["learning_outcome"][concept]:
            options["learning_outcome"][concept][blooms_level] = []

        options["learning_outcome"][concept][blooms_level].append(outcome)
    return options


def generate_question(selected_outcome) -> object:
    # Generates question based on selected Learning outcome
    prompt = f"You are a Javascript tutor. Following is the learning outcome expected out of the question: \n{selected_outcome} " \
             f"Generate a closed ended QUESTION that can be evaluated OBJECTIVELY." \
             f"Also, IN ADDITION TO the question asked, ALWAYS ASK FOR EXAMPLES from the user." \
             f"No need to mention the type of question you are asking. No need to mention Q or Question before the question."

    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=prompt,
        temperature=0.7,
        max_tokens=50,
        stop=None
    )

    generated_question = response.choices[0].text.strip()
    #print(generated_question)
    return generated_question


def generate_feedback(chat_history: list[dict]) -> object:
    # Generates feedback based on chat history
    model = "gpt - 4.turbo",
    prompt = "You are a tutor assisting a student in an interactive learning session." \
             "You should evaluate the student's responses as Not Aceptable, Satisfactory, or Proficient ONLY when a genuine attempt at answering is made. DO NOT judge otherwise" \
             "If the student's response is off-topic, seeking clarification, or unrelated, provide guidance or prompt them to address the question but DO NOT judge." \
             "The following is the chat history between you and the leaner. \n Chat history: "

    for chat in chat_history:
        string_to_append = "{role}:{Message} \n".format(role=chat["role"], Message=chat["content"])
        prompt += string_to_append
    prompt += "Assistant: "
    feedback = openai.Completion.create(
        engine="text-davinci-003",
        temperature=0.5,
        prompt=prompt,
        max_tokens=100
    )

    generated_feedback = feedback.choices[0].text.strip()
    # print(generated_feedback)
    return generated_feedback


def main():
    openai.api_key = openai_key

    options = get_options()
    st.title("Javascript let's go!")

    # Add a sidebar for options
    st.sidebar.title("Options")
    selected_topic = st.sidebar.selectbox('Choose Topic', options["Topic"])
    selected_subtopic = st.sidebar.selectbox('Choose Subtopic', options["SubTopic"])
    selected_concept = st.sidebar.selectbox('Choose Concept', options["Subtopic-concept_dictionary"][selected_subtopic])
    selected_blooms = st.sidebar.selectbox("Choose Bloom's level", options["Blooms"])

    # Update UI dynamically based on selections
    outcome = options["learning_outcome"].get(selected_concept, {}).get(selected_blooms, [])
    selected_outcome = st.sidebar.selectbox('Choose Learning Outcome', outcome)

    start_label = "Start Training"

    # Display the main content based on the options
    with st.form("TrainingForm"):
        st.write(f"**Topic:** {selected_topic}")
        st.write(f"**Subtopic:** {selected_subtopic}")
        st.write(f"**Concept:** {selected_concept}")
        st.write(f"**Bloom's level:** {selected_blooms}")
        st.write(f"**Learning Outcome:** {selected_outcome}")
        started = st.form_submit_button(start_label)

    # creating messages (a list of dictionaries)
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # creating question when the Start Training button is turned on and adding it to chat history
    if started:
        st.session_state.messages = []
        st.session_state.messages.append({"role": "Assistant", "content": generate_question(selected_outcome)})

    # Taking user's input and getting the question generated
    if prompt_user := st.chat_input("Your Answer"):
        st.session_state.messages.append({"role": "User", "content": prompt_user})
        st.session_state.messages.append({"role": "Assistant", "content": generate_feedback(st.session_state.messages)})

    # displaying the chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])


if __name__ == "__main__":
    main()
