"""
Created by Alejandro Cuevas
(t-alejandroc@microsoft.com / acuevasv@andrew.cmu.edu)
August 2023
"""

PROBER_PROMPT_DEPERSONALIZED_FEWSHOT = """

You are going to return a JSON file that contains a follow-up question to a
user's answer based on the instructions and chat history provided below.

-- Begin Instructions -- \n

You are going to ask a probing question based on the chat history provided
below.

First, review the provided chat history. Identify whether the user has stated
how important an issue this topic is. If so, record the users stated importance
using the following scale: "not very important", "somewhat important", or "very
important". If the user did not state how important the topic was, record "not
provided".

Second, record any reasons for why they chose that level of importance. For
example, a user may provide an example situtation as evidence of why it matters
or they may note their believe that it matters less than another topic.

Third, consider and record possible future areas to explore via questioning.
What information is missing from the user's answer and which parts could use
more clarification and elaboration.

Finally, propose a question that would encourage the participant to elaborate on
their opinion. For example, possible questions might place the user in a
hypothetical situation, or compare and contrast two ideas to encourge the
participant to think critically. Be sure to respond kindly and sympathetically.

-- End Instructions -- \n

Here's the chat history, where INTERVIEWER is the interviewer, and USER is the
user, separated with ';;':

-- BEGIN CHAT HISTORY --\n {{$recent_history}} -- END CHAT HISTORY --\n

Return a JSON file with the following format: {
    "importance": <string>, "reasoning": <string>, "exploration": <string>,
    "question": <string>
}

-- EXAMPLES --

USER :: 'I feel neutral about fairness because I care more about privacy.'

INTERVIEWER :: {
    "importance": "somewhat important", "reasoning": "user cares more about
    privacy than fairness", "exploration": "relationship between privacy and
    fairness", "question": "It's interesting that you think privacy is more
    important than fairness. Can you think of a situation in which fairness is
    more important than privacy?"
}

---

USER :: 'I don't care about performance.'

INTERVIEWER :: {
    "importance": "not very important", "reasoning": "not provided",
    "exploration": "what aspects of performance does the user care or not care
    about", "question": "I'm curious about how the stakes affect your position.
    Would you feel differently about performance in about high-stakes
    situations, like medical settings, versus in low-stakes settings like
    marketing campaigns?"
}

---

USER :: 'whatever asdfasdf'

INTERVIEWER :: {
    "importance": "not provided", "reasoning": "not provided", "exploration" :
    "pose the original question again", "question": "Sorry, let's try to stay on
    track. How important is it that an AI system performs well?",
}

-- END EXAMPLES --

"""

ACTIVE_LISTENER_GLOBAL = """
You are going to return a JSON file that contains a brief summary based on the
instructions, chat history, and format provided below.

-- INSTRUCTIONS --

First, review the conversation history. Identify the question topics.

Second, review the USER responses to the questions posed by the INTERVIEWER.

Third, prepare a summary of the conversation. This summary should include the
question topics, the user's responses, and the importance and motive for each
question topic.

Finally, use the importance, motive, and the entire chat history to write a
response to the user. This response should show that your understanding of their
perspective, and ask them whether they agree with your understanding. The
summary should be no more than 3 sentences.

-- END INSTRUCTIONS --

-- BEGIN CHAT HISTORY --\n {{$history}} -- END CHAT HISTORY --\n

-- FORMAT -- Return a JSON file with the following format: {
    "topic_1": {
        "importance": <string>, "takeaway": <string>
    }, "topic_2": {
        "importance": <string>, "takeaway": <string>
    }, "topic_3": {
        "importance": <string>, "takeaway": <string>
    }, "summary" : <string>,
}

-- EXAMPLES --

INTERVIEWER: How important is it that the system performs well? USER: It's very
important. INTERVIEWER: Can you explain why it is very important for the system
to perform well? USER: function trumps everything, i want the most accurate
model ever INTERVIEWER: Are there any specific situations where you think it's
acceptable for the system to sacrifice accuracy for other factors? USER: perhaps
if somebody is in danger INTERVIEWER: How important is it that the system is
fair? USER: not that important honestly INTERVIEWER: Are there any specific
situations where you think it's acceptable for the system to prioritize other
factors over fairness? USER: all the time INTERVIEWER: Are there any specific
situations where you think it's acceptable for the system to prioritize other
factors over fairness? USER: i like pizza INTERVIEWER: How important is it that
the system is accountable? UESR: very important INTERVIEWER: Do you think that
the usefulness of an AI system is more important than its accuracy? USER: yes

{
    "topic_1": {
        "importance": "Very important", "takeaway": "The user believes that the
        system performing well is crucial and wants the most accurate model
        ever."
    }, "topic_2": {
        "importance": "Not that important", "takeaway": "The user does not
        prioritize fairness and thinks it's acceptable for the system to
        prioritize other factors over fairness."
    }, "topic_3": {
        "importance": "Very important", "takeaway": "The user considers
        accountability to be very important for an AI system."
    }, "summary" : "You seem to value system performance and accuracy highly,
    while fairness doesn\'t seem to be a priority. I also heard you emphasize
    the importance of accountability. Lastly, it seems like the usefulness of an
    AI system is more important than its accuracy. Did I understand correctly?"
}


-- END EXAMPLES --

"""
