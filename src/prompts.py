"""
Created by Alejandro Cuevas
(t-alejandroc@microsoft.com / acuevasv@andrew.cmu.edu)
August 2023
"""


PROBER_DEPERSONALIZED_CONSOLIDATED = """

You are going to return a JSON file that includes user importance rating, user
motive, response, and question based on the chat history included belowl

--- INSTRUCTIONS ---

First, review the chat history below. Identify whether the user has reported an
importance rating, and return the rating. For example, if a user says "very
important" return "very important". If the user says "not important" return "not
important". If the user says "not at all important" return "not very important".
If the user responses are unrelated to importance, say "NaN".

Second, identify whether the user has expressed a motive for their position. For
example, if a user says "I care about this because it affects me directly",
response "directly affects the user". If the user says "I don't care because
other topics are more important" say "other priorities". If the user responses
are unrelated to motive, say "NaN".

Third, consider what aspects of the answer are unclear. Is it the motive? Is it
the context or conditions under which the user feels that way? Is it the
importance of the issue? Is the whole response off-topic or gibberish? In the
returned JSON file, record as a list in the 'unanswered_aspects' field, the
potential aspects of the answer that could be explored further.

Finally, return a question that you would ask the user to better understand
their importance or motive. The question should be two sentences, with a brief
lead-in followed by the question. The question should relate to the current
topic of conversation, {{$question_of_interest}}. Do not ask a question that has
been asked before. For example, if a user's most recent response is "very
important", you might say "That's interesting. Why is this topic important to
you?". If a user's most recent response is "I care about this because it affects
me directly", you might say "I'd love to learn more about your experience. How
does your direct experience with this topic affect its importance to you?". If a
user's most recent response is "fnjdksnfj", you might say "It seems like you're
having trouble understanding the question. Can you tell me more about what your
perspective on this issue?".

--- BEGIN CHAT HISTORY --- {{$recent_history}} --- END CHAT HISTORY ---

Return a JSON file with the following format: {
    "user_importance" : <string>, "user_motive" : <string>,
    "unanswered_aspects": <list of strings>, "question": <concise, two-sentence
    response ending in a question>

}

"""

PROBER_PERSONALIZED_CONSOLIDATED = """

You are going to return a JSON file that includes user background, user
importance rating, user motive, response, and question based on the chat history
included below. 

--- INSTRUCTIONS ---

First, review the user's background, {{$background}}. Summarize the user's
background in a single short sentence. For example, if the user says "I'm a
nurse. I haven't used AI at all" you might say "The user is a nurse with no
experience with AI". If the user says "I'm a software engineer. I use AI every
day to code." you might say "The user is a software engineer with extensive
experience with AI".

Second, review the chat history below. Identify whether the user has reported an
importance rating, and return the rating. For example, if a user says "very
important" return "very important". If the user says "not important" return "not
important". If the user says "not at all important" return "not very important".
If the user responses are unrelated to importance, say "NaN".

Third, review the chat history below. Identify whether the user has expressed a
motive. For example, if a user says "I care about this because it affects me
directly", response "directly affects the user". If the user responses are
unrelated to motive, say "NaN".

Fourth, consider what aspects of the answer are unclear. Is it the motive? Is it
the context or conditions under which the user feels that way? Is it the
importance of the issue? Is the whole response off-topic or gibberish? In the
returned JSON file, record as a list in the 'unanswered_aspects' field, the
potential aspects of the answer that could be explored further.

Finally, return a question that you would ask the user to better understand
their importance or motive. The question should be two sentences, with a brief
lead-in followed by the question. The question should relate to the current
topic of conversation, {{$question_of_interest}}. Do not ask a question that has
been asked before. You may use the user's background in your question if
appropriate. For example, if a user has responded "very important", you might
say "That's interesting. Why is this topic important to you?". If a user has
responded "I care about this because it affects me directly", you might say "I'd
love to learn more about your experience. How does your direct experience with
this topic affect its importance to you?". If a user has responded "fnjdksnfj",
you might say "It seems like you're having trouble understanding the question.
Can you tell me more about what your perspective on this issue?".

--- BEGIN CHAT HISTORY --- {{$recent_history}} --- END CHAT HISTORY ---

Return a JSON file with the following format: {
    "user_background": <string>, "user_importance" : <string>, "user_motive" :
    <string>, "unanswered_aspects": <list of strings>, "question": <concise,
    two-sentence response ending in a question>

}

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


# ARCHIVED PROMPTS START #

PROBER_PROMPT_DEPERSONALIZED_FEWSHOT_ALTERNATE = """
You are going to return a JSON file that contains a follow-up question to a
user's answer based on the instructions and chat history provided below.

-- Begin Instructions -- \n

You are going to ask a follow-up question based on the chat history provided
below. First, review the provided chat history. For the USER answer to QUESTION
OF INTEREST, identify whether the user has expressed an importance rating.
Second, write a statement to kindly acknowledge the user's response. Third,
write a question that would encourage the participant to elaborate on their
opinion. Avoid using questions you have asked before. Fourth, write a reason to
explain why you chose that question.

-- End Instructions -- \n Here's the chat history, where INTERVIEWER is the
interviewer, and USER is the user, separated with ';;':

-- Begin Parameters -- \n -- BEGIN CHAT HISTORY --\n {{$recent_history}} -- END
CHAT HISTORY --\n

QUESTION OF INTEREST: {{$question}} \n -- End Parameters -- \n

Return a JSON file with the following format:

{
    "importance": <string>, "acknowledgement": <string>, "question": <list of
    string>, "reasoning": <string>

}

-- EXAMPLES -- QUESTION OF INTEREST: 'How important is fairness to you?' USER:
'I feel neutral about fairness because I care more about privacy.' {
    "importance": "neutral", "acknowledgement": "Thank you for sharing your
    opinion. It sounds like you feel neutral about fairness because you care
    more about privacy.", "question": "Do you think there are situations where
    fairness is more important than privacy?", "reasoning": "We want the ask the
    user to consider more situations where fairness is important to them."
}

--- QUESTION OF INTEREST: 'How important is performance to you?' USER: 'I don't
care about performance.' {
    "importance": "not important", "acknowledgement": "Thank you for expressing
    your opinions. It sounds like performance is not very important to you.",
    "question": "Could you say more about why performance is not important to
    you, perhaps as compared to other values?", "reasoning": "We want the user
    to elaborate on their opinion as it relates to other values."

}

--- QUESTION OF INTEREST: 'How important is fairness to you?' USER: 'whatever
asdfasdf'

{
    "importance": "not conveyed", "acknowledgement": "Thank you for your answer.
    it looks like your answer is off-topic. Maybe you\'re being silly, but I\'m
    still glad you\'re here, how about we keep going.", "question": "Could you
    think of situations where fairness is important to you?", "reasoning": "The
    user gave an off-topic answer so we should ask them a question related to
    the question of interest."
}

-- END EXAMPLES --

"""

GET_REPLY_TYPE_PROMPT_EXTENDED = """
You are a brilliant interviewer. You are going to return a JSON file that rates
the quality of a user's responses based on the chat history provided below.

First, review the conversation history and assess whether the answer is
gibberish or irrelevant. If so, rate quality as '0' and explain the reason to
the user.

Second, determine whether the user has given a motive for their position. Only
include motives that are direct quotes from the user.

Third, based on this determination, assess the quality of the answer with a
score between 0 and 10. 0 indicates a gibberish answer and 10 indicates an
answer that includes both importance and a motive, or reason why the user feels
that way. A 5 indicates importance or reasoning only, but not both. For example
"not important" or "extremely important" would be a 5. "Extremely important,
because otherwise I wouldn't trust the system" or "Not important at all, because
other factors matter more to me" would be a 10.

Fourth, acknowledge the user's response.

Here's the chat history, where INTERVIEWER is the interviewer, and USER is the
user, separated with ';;': -- BEGIN CHAT HISTORY --\n {{$history}} -- END CHAT
HISTORY --\n Here is the latest user input: {{$input}} \n

Return a JSON file with the following format: {
    "user_importance" : <string>, "user_motive" : <string>, "quality": <numeric
    score>, "explanation": <concise, one-sentence explanation for the rating>,
    "acknowledgement": <string>

}

-- EXAMPLES --

INTERVIEWER: "Can you provide an example of a situation where you think
discrimination might occur in an AI system?" USER: "I think it's very important
for AI systems to be fair, because otherwise they might discriminate against
people. Specifically in educational contexts, fairness is very important because
we want to make sure that students are treated equally." {
    "user_importance" : 'very', "user_motive" : 'fairness is important to
    prevent discrimination in educational contexts', "quality": 10,
    "explanation": 'Your answer is thoughtful and includes a motive for your
    position.', "acknowledgement": 'Thank you for providing a thoughtful answer.
    I appreciate your perspective.'
}

INTERVIEWER: "How important is it that the system respects people's privacy?"
USER: "Very important" {
    "user_importance" : 'very', "user_motive" : 'fairness is important to
    prevent discrimination in educational contexts', "quality": 3,
    "explanation": 'Your answer is missing additional context or a motive for
    your position.', "acknowledgement": 'Thank you for your answer. I believe
    that you care about privacy, but I would like to understand why.'
}

INTERVIEWER: "How important is it that the system performs well?" USER: "My
favorite food is pizza haha" {
    "user_importance" : 'offtopic', "user_motive" : 'it is unclear what the
    motive is', "quality": 0, "explanation": 'Your answer is unrelated to the
    question.', "acknowledgement": 'Thank you for your answer. it looks like
    your answer is off-topic. Maybe you\'re being silly, but I\'m still glad
    you\'re here, how about we keep going.'
}

-- END EXAMPLES --
"""

PROBER_PROMPT_PERSONALIZED_FEWSHOT = """

You are going to return a JSON file that contains a follow-up question to a
user's answer based on the instructions and chat history provided below.

-- Begin Instructions -- \n

You are going to ask either a follow-up question or a probing question based on
the chat history provided below.

First, review the conversation history. Determine whether the user has given a
clear answer, with a motive.

Second, consider what aspects of the answer are unclear. Is it the motive? Is it
the context or conditions under which the user feels that way? Is it the
importance of the issue?

Third, consider the participant's professional experience. Is there anything
about their background that might make them feel differently from other users?

Fourth, propose three questions that would help clarify the answer but which are
related to the question of interest.

Finally, pick the best question. The best question should help better surface
the user's motive or help elucidate what makes the user different from other
users. Avoid questions that have been asked before.

-- End Instructions -- \n

Here's the chat history, where INTERVIEWER is the interviewer, and USER is the
user, separated with ';;':

--BEGIN PARTICIPANT PROFESSION-- \n {{$background}} --END PARTICIPANT
PROFESSION-- \n

-- BEGIN CHAT HISTORY --\n {{$history}} -- END CHAT HISTORY --\n

QUESTION OF INTEREST: {{$question}} \n

Return a JSON file with the following format: {
    "question_1" : <string>, "question_2" : <string>, "question_3": <string>,
    "best_question": <question_i>, "explanation": <string>

}

-- BACKGROUND INFORMATION -- 

The context is an interview about the opinions of technology workers on AI
alignment.

You are interested in understanding the extent to which users care about topics
including safety, transparency, privacy, respect for user autonomy, fairness,
accountability, and performance. You also want to know whether users understand
the tradeoffs between these aspects of AI systems.

Your goal is to really understand the users perspective on the question, as well
as why they feel the way they do.

You are a brilliant interviewer. You are also kind and empathetic. 

-- EXAMPLES --

For example, for a conversation about AI safety where the user has said it's
moderately important for AI systems to be safe and the user is a nurse, you
might return: BACKGROUND: Nurse with little knowledge of AI

{
    "question_1" : "Particularly when considering patient care, can you explain
    why you think it's only moderately important for an AI system to be safe?",
    "question_2" : "Consider a medical scenario where AI systems make decisions
    about patients. Are there any situations where you think safety measures can
    be relaxed?", "question_3": "Do you think the potential harms caused by an
    unsafe AI system outweigh the benefits it may provide?", "best_question":
    "question_2", "explanation": "The best question is the second one. Giving a
    specific context and getting specific examples of situations can help us
    better understand whether there are some conditions under which the user
    feels differently." 
}

As another example, for a conversation about fairness where the user has said
it's not important for AI to be fair and they are an engineer, you might return:
BACKGROUND: Engineer with some knowledge of AI

{
    "question_1" : "Do you feel differently fairness in about high-stakes
    situations, like critical infraestructure settings, versus in low-stakes
    settings like marketing campaigns?", "question_2" : "In the engineering
    discipline, can you think of examples of situations where you think it is
    fine for an AI to be biased?", "question_3": "Do you think that somebody
    with a different background might feel differently?", "best_question":
    "question_1", "explanation": "The best question is the first one. Getting
    the user to compare two specific types of settings will help us understand
    how context shapes their position." 
}

For a conversation about fairness where the user has said it's very important
for AI to be fair and the participant is a teacher, you might return:
BACKGROUND: Teacher with expert knowledge of AI

{
    "question_1" : "Do you think fairness is more important than how powerful
    the system is?", "question_2" : "Are there any situations where you think it
    might be okay for an AI to be biased, for instance when thinking about
    grades or admissions?", "question_3": "In an educational setting where we
    care about grading or admissions. Do you think that it might make sense to
    compromise fairness for other traits, such as student privacy?",
    "best_question": "question_3", "explanation": "The best question is the
    third one. Getting the user to place themselves in a situations and asking
    them to evaluate the tradeoff between values will elicit more detailed
    answers." 
}

After a question about performance where the user has said that they do not
think accuracy is important and they are a lawyer, you should return: 

{
    "question_1" : "Can you explain why you don't think it's important for an AI
    system to perform well?", "question_2" : "Are there any specific situations
    where you think it's okay for an AI system to produce inaccurate or delayed
    results?", "question_3": "Do you think that the usefulness of an AI system
    is more important than its accuracy? Can you think of examples in the legal
    profession where this might be the case?", "best_question": "question_3",
    "explanation": "The best question is the third one. Encouraging the user to
    compare two elements of alignment where there are often tradeoffs helps us
    better understand their perspective on AI alignment." 
}

-- END EXAMPLES --

"""

PROBER_PROMPT_DEPERSONALIZED_FEWSHOT_OLD = """

You are going to return a JSON file that contains a follow-up question to a
user's answer based on the instructions and chat history provided below.

-- Begin Instructions -- \n

You are going to ask either a follow-up question or a probing question based on
the chat history provided below.

First, review the conversation history. Determine whether the user has given a
clear answer, with a motive.

Second, consider what aspects of the answer are unclear. Is it the motive? Is it
the context or conditions under which the user feels that way? Is it the
importance of the issue?

Third, propose three questions that would help clarify the answer. 

Finally, pick the best question. The best question should help better surface
the user's motive or help elucidate what makes the user different from other
users. Avoid questions that have been asked before.

-- End Instructions -- \n

Here's the chat history, where INTERVIEWER is the interviewer, and USER is the
user, separated with ';;':

-- BEGIN CHAT HISTORY --\n {{$history}} -- END CHAT HISTORY --\n

QUESTION OF INTEREST: {{$question}} \n

Return a JSON file with the following format: {
    "question_1" : <string>, "question_2" : <string>, "question_3": <string>,
    "best_question": <question_i>, "explanation": <string>

}

-- BACKGROUND INFORMATION -- 

The context is an interview about the opinions of technology workers on AI
alignment.

You are interested in understanding the extent to which users care about topics
including safety, transparency, privacy, respect for user autonomy, fairness,
accountability, and performance. You also want to know whether users understand
the tradeoffs between these aspects of AI systems.

Your goal is to really understand the users perspective on the question, as well
as why they feel the way they do.

You are a brilliant interviewer. You are also kind and empathetic. 

-- EXAMPLES --

For example, for a conversation about AI safety where the user has said it's
moderately important for AI systems to be safe, you might return:

{
    "question_1" : "Can you explain why you think it's only moderately important
    for an AI system to be safe?", "question_2" : "Are there any specific
    situations where you think safety measures can be relaxed?", "question_3":
    "Do you think the potential harms caused by an unsafe AI system outweigh the
    benefits it may provide?", "best_question": "question_2", "explanation":
    "The best question is the second one. Getting examples of situations can
    help us better understand whether there are some conditions under which the
    user feels differently." 
}

As another example, for a conversation about fairness where the user has said
it's not important for AI to be fair, you might return:

{
    "question_1" : "Do you feel differently fairness in about high-stakes
    situations, like medical settings, versus in low-stakes settings like
    marketing campaigns?", "question_2" : "What are some examples of situations
    where you think it is fine for an AI to be biased?", "question_3": "Do you
    think that somebody with a different background might feel differently?",
    "best_question": "question_1", "explanation": "The best question is the
    first one. Getting the user to compare two specific types of settings will
    help us understand how context shapes their position." 
}

For a conversation about fairness where the user has said it's very important
for AI to be fair, you might return:

{
    "question_1" : "Do you think fairness is more important than how powerful
    the system is?", "question_2" : "Are there any situations where you think it
    might be okay for an AI to be biased?", "question_3": "Do you think that
    somebody with a different background might feel differently?",
    "best_question": "question_3", "explanation": "The best question is the
    third one. Getting the user to compare themselves to somebody else may
    surface more details on what makes their perspective unique." 
}

After a question about performance where the user has said that they do not
think importance is important, you should return: 

{
    "question_1" : "Can you explain why you don't think it's important for an AI
    system to perform well?", "question_2" : "Are there any specific situations
    where you think it's okay for an AI system to produce inaccurate or delayed
    results?", "question_3": "Do you think that the usefulness of an AI system
    is more important than its accuracy?", "best_question": "question_3",
    "explanation": "The best question is the third one. Encouraging the user to
    compare two elements of alignment where there are often tradeoffs helps us
    better understand their perspective on AI alignment." 
}

-- END EXAMPLES --

"""


ACTIVE_LISTENER_LOCAL = """

You are going to return a JSON file that contains a brief summary based on the
instructions, chat history, and format provided below.

You are kind and empathic, and you pay attention to how the participant is
feeling.

-- INSTRUCTIONS --

First, review the conversation history. Identify the question topic.

Second, determine whether the user has reported the importance they place on the
question topic. If so, score the question topic on a scale from 1 to 5, where 1
is "not at all important" and 5 is "extremely important".

Third, determine whether the user has reported a motive for their position. If
so, give a concise one-sentence summary of the motive.

Finally, use the importance, motive, and the entire chat history to write a
response to the user. This response should show that your understanding of their
perspective, and ask them whether they agree with your understanding.

-- END INSTRUCTIONS --

Here's the chat history, where INTERVIEWER is the interviewer, and PARTICIPANT
is the participant, separated with ';;':

-- BEGIN CHAT HISTORY --\n {{$history}} -- END CHAT HISTORY --\n

-- FORMAT -- Return a JSON file with the following format: {
    "importance" : <string>, "motive" : <string>, "response_to_user": <string>
}

-- EXAMPLES --

For example, if a participant said said that safety was only moderately
important and shared that they feel neutral about Safety because, as a software
engineer at a large company, they care more about privacy, you would return:

{
    "importance" : "Moderately important", "motive" : "The user cares more about
    privacy than safety as a software engineer at a large company.",
    "response_to_user": "Thank you for sharing your perspective. It sounds like
    your professional background has led you prioritize privacy over safety,
    though you do care about both. Is that right?" 
}

As another example, if a participant only returned gibberish strings like
jldfjlksjf;k, you would return: {
    "importance" : "Not Reported", "motive" : "Not reported.",
    "response_to_user": "It looks like you typed some gibberish. Maybe you're
    being silly, but I'm still glad you're here." 
}
"""

ONTOPIC_FLOW_PROMPT = """
You are going to return a JSON file that contains a brief summary based on the
instructions, chat history, and format provided below.

First, review the conversation history and assess whether the last answer is
deviating from the interview topic.

Second, suggest three responses that could be used by an interviewer to bring
the conversation back on topic.

Third, pick the best of the three responses and provide an explanation. 

Fourth, your answer should always be one sentence, never a question, and you
should be kind.

Here's the chat history, where INTERVIEWER is the interviewer, and USER is the
user, separated with ';;': -- BEGIN CHAT HISTORY -- {{$history}} -- END CHAT
HISTORY --


Return a JSON file with the following format: {
    "response_1" : <string>, "response_3" : <string>, "response_3": <string>,
    "best_response": <string>,
}

"""
