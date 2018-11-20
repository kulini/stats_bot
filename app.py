import os
import time
import re
import csv
from slackclient import SlackClient

# instantiate Slack client
slack_client = SlackClient(os.environ.get('SLACK_BOT_TOKEN'))
# starterbot's user ID in Slack: value is assigned after the bot starts up
starterbot_id = None

# constants
RTM_READ_DELAY = 1 # 1 second delay between reading from RTM
QUESTION_COMMAND = "quiz me"
ANSWER_COMMAND = "answer"
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"

print("I'm here")

def parse_bot_commands(slack_events):
    """
        Parses a list of events coming from the Slack RTM API to find bot commands.
        If a bot command is found, this function returns a tuple of command and channel.
        If its not found, then this function returns None, None.
    """
    for event in slack_events:
        # print(event)
        if event["type"] == "message" and not "subtype" in event:
            user_id, message = parse_direct_mention(event["text"])
            # print(user_id)
            # print(starterbot_id)
            if user_id == starterbot_id:
                # print(message) # e.g. "quiz me"
                # print(event)
                return message, event["channel"]
    return None, None

def parse_direct_mention(message_text):
    # print(message_text)
    """
        Finds a direct mention (a mention that is at the beginning) in message text
        and returns the user ID which was mentioned. If there is no direct mention, returns None
    """
    matches = re.search(MENTION_REGEX, message_text)
    # the first group contains the username, the second group contains the remaining message
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)

def handle_command(command, channel):
    """
        Executes bot command if the command is known
    """
    # Default response is help text for the user
    default_response = "Not sure what you mean. Try *{}*.".format(QUESTION_COMMAND)

    # Finds and executes the given command, filling in response
    response = None
    # This is where you start to implement more commands!
    if command.endswith("?"):
        command = command[:-1]
        # print(f"command is {command}")
    parsed_command = command.lower().split(" ")
    print(f"parsed_command: {parsed_command}")
    # Extract the question number

    question_number = parsed_command[-1]

    print(f"The question number is {question_number}")
    if "quiz" or "ask" in parsed_command:
        # Call function to return question from a database
        q_or_a = "q"
    if "answer" in parsed_command:
        # print("answer")
        q_or_a = "a"

    response = return_response(question_number, q_or_a)

    # Sends the response back to the channel
    slack_client.api_call(
        "chat.postMessage",
        channel=channel,
        text=response or default_response
    )

def return_response(number, q_or_a):
    question_number = str(number)

    # print(f"q_or_a: {q_or_a}")

    question_bank = {
        '1': "Calculate the variance of the following dataset: [37, 25, 40, 21, 16, 25, 19]",
        '2': "Express variance as a mathematical formula.",
        '3': "What is the notation for the standard deviation of a sample?"
    }

    answer_bank = {
        '1': 70.4,
        '2': 'https://d1ca4yhhe0xc0x.cloudfront.net/Files/474/9/DefVarEqn.jpg',
        '3': 's'
    }

    if q_or_a == "q":
        # print("q")
        return question_bank[question_number]
    if q_or_a == "a":
        # print("a")
        return answer_bank[question_number]

if __name__ == "__main__":
    if slack_client.rtm_connect(with_team_state=False):
        print("Starter Bot connected and running!")
        # Read bot's user ID by calling Web API method `auth.test`
        starterbot_id = slack_client.api_call("auth.test")["user_id"]
        while True:
            command, channel = parse_bot_commands(slack_client.rtm_read())
            if command:
                # print(channel)
                handle_command(command, channel)
            time.sleep(RTM_READ_DELAY)
    else:
        print("Connection failed. Exception traceback printed above.")
