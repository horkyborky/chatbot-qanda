# chatbot-qanda

Alternate question (or utterance) generator for chatbots.  Frequently, if you're creating chatbots based on a set of questions and answers, one of the big problems is pre-populating
alternate ways of asking those questions.  Generally in the past, I've approached this manually, either tasking staffers (or doing it myself) or crowdsourcing through mTurk or SurveyMonkey
or similar.

Given a CSV file with the header rows - questions, answers, notes (optional), this script will parse the file and send the questions over to an LLM (in this case GPT-X) to create alts, then dump the results out to a file.

You can alter the system prompt as appropriate for your use case.
