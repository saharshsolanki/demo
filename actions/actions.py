import json
from typing import Any, Text, Dict, List

import requests
from rasa_sdk import Action, Tracker, FormValidationAction
from rasa_sdk.events import SlotSet, ActionExecuted, UserUttered, ActiveLoop, EventType
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.forms import FormAction, REQUESTED_SLOT
from rasa_sdk.types import DomainDict

help = [{'command': "/login", 'message': "Use To Login To User JIRA Account "},
        {'command': "projects", 'message': "used to show your JIRA Account Porjects "},
        {'command': "/set_wroking_env", 'message': "Set Working Key << Use This To Set The Current Working Project  "},
        {'command': "Show Issue ", 'message': "Used To Show the Issues Of Your Account"},
        {'command': "create issue", 'message': "Use This To create a Issue "}
        ]


def login_check(email, password):
    url = "https://saharshsolanki1.atlassian.net/rest/api/2/project"
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    query = {

    }

    response = requests.get(url, headers=headers, params=query,
                            auth=(email, password))
    if response.status_code == 200:
        return True
    else:
        return False


class Actionskprojectkey(FormAction):

    def name(self) -> Text:
        return "action_ask_project_key"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        if tracker.get_slot("email") is None:
            dispatcher.utter_message(text="You Have Not Logged In")
            return self.deactivate()
        elif tracker.get_slot("api_key") is None:
            dispatcher.utter_message(text="You Have Not Logged In")
            return self.deactivate()
        else:
            email_id = tracker.get_slot('email')
            api_key = tracker.get_slot("api_key")
            url = "https://saharshsolanki1.atlassian.net/rest/api/2/project"
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json"
            }
            query = {}
            response = requests.get(url, headers=headers, params=query,
                                    auth=(email_id, api_key))
            data = response.json()
            total = 0
            keys = ""
            button = []
            for d in data:
                project_name = d['name']
                project_key = d['key']
                total = total + 1
                keys = keys + project_key + ","
                button.append({'title': project_name, 'payload': project_key})

            dispatcher.utter_message("You Have " + str(total) + " Projects And Keys Are " + keys)
            dispatcher.utter_button_message(text="Enter Or Select Your PROJECT KEY",
                                            buttons=button)
            return []


class ValidateProjectKey(FormValidationAction):

    def name(self) -> Text:
        return "validate_project_key_form"

    def validate_project_key(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:


        project = slot_value
        email_id = tracker.get_slot('email')
        api_key = tracker.get_slot('api_key')
        url = "https://saharshsolanki1.atlassian.net/rest/api/3/search"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

        query = {
            'jql': 'project = ' + project
        }

        response = requests.get(url, headers=headers, params=query,
                                auth=(email_id, api_key))
        if response.status_code == 200:
            dispatcher.utter_message(text="Now i Will Use " + project + " As Working Project")
            return {"project_key": slot_value}
        else:
            dispatcher.utter_message(text="I Can't Verify This Key In Jira")
            return {"project_key": None}


# Start

class Actionaskissue_key_for_delete(FormAction):

    def name(self) -> Text:
        return "action_ask_issue_key_for_delete"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        if tracker.get_slot("email") is None:
            dispatcher.utter_message(text="Please Login")
            dispatcher.utter_button_message(text="Want to login ?",
                                            buttons=[{'title': 'Lets login', 'payload': "login"}])
            return self.deactivate()

        elif tracker.get_slot("api_key") is None:
            dispatcher.utter_message(text="Please Login")
            dispatcher.utter_button_message(text="Want to login ?",
                                            buttons=[{'title': 'Lets login', 'payload': "login"}])
            return self.deactivate()

        elif tracker.get_slot("project_key") is None:
            dispatcher.utter_message(text="I Dont't Know In Which Project You Are Working ")
            dispatcher.utter_button_message(text="Want Add Working project key ?",
                                            buttons=[{'title': 'Set Project', 'payload': 'set working project key'}])
            return self.deactivate()
        else:


            email_id = tracker.get_slot('email')
            api_key = tracker.get_slot("api_key")

            url = "https://saharshsolanki1.atlassian.net/rest/api/3/search"
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json"
            }

            query = {
                'jql': 'project = ' + tracker.get_slot("project_key")
            }

            response = requests.get(url, headers=headers, params=query,
                                    auth=(email_id, api_key))
            data = response.json()

            issues = data["issues"]
            if len(issues) is 0:
                dispatcher.utter_message(text="You don't have any issue")
                dispatcher.utter_message(text="Want to create issue",buttons=[{'title':"Create issue",'payload':"create issue"}])
                return self.deactivate()
            else:
                dispatcher.utter_message(text="Which issue you want to delete ?")
                buttons = []
                for issue in issues:
                    try:
                        issue_title = issue['fields']['summary']
                        issue_key = issue['key']
                        buttons.append({'title':issue_title,'payload':issue_key})
                    except:
                        issue_id = issue['id']
                        dispatcher.utter_message(text="I Got Error While Loading This Issue ID :" + issue_id)
                dispatcher.utter_button_message(text="Select or Enter issue key",buttons=buttons)
                return []


class Validateissue_deletion_from(FormValidationAction):

    def name(self) -> Text:
        return "validate_issue_deletion_from"

    def validate_issue_key_for_delete(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:

        issue_id = slot_value
        email_id = tracker.get_slot('email')
        api_key = tracker.get_slot("api_key")
        url = "https://saharshsolanki1.atlassian.net/rest/api/3/issue/" + issue_id
        response = requests.request("DELETE", url, auth=(email_id, api_key))

        if response.status_code == 204:
            dispatcher.utter_message(text="The issue is deleted successfully")
            return {"issue_key_for_delete": None,'requested_slot':None}
        elif response.status_code == 403:
            dispatcher.utter_message(text="You don't have permision to delete this issue")
            return {"issue_key_for_delete": None,'requested_slot':None}
        else:
            dispatcher.utter_message(text="Either issue not found or you don't have persion to delete")
            return {"issue_key_for_delete": None,'requested_slot':None}


# End


class ActionCreateIsssuess(FormAction):

    def name(self) -> Text:
        return "action_ask_issue_summary"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        if tracker.get_slot("email") is None:
            dispatcher.utter_message(text="You Have Not Logged In")
            dispatcher.utter_button_message(text="Want To login ?",
                                            buttons=[{'title': 'Login', 'payload': 'login'}])
            return self.deactivate()
        elif tracker.get_slot("api_key") is None:
            dispatcher.utter_message(text="You Have Not Logged In")
            dispatcher.utter_button_message(text="Want To login ?",
                                            buttons=[{'title': 'Login', 'payload': 'login'}])
            return self.deactivate()
        elif tracker.get_slot("project_key") is None:
            dispatcher.utter_message(text="I Dont't Know In Which Project You Are Working ")
            dispatcher.utter_button_message(text="Want To login ?",
                                            buttons=[{'title': 'Login', 'payload': 'login'}])
            return self.deactivate()
        else:
            dispatcher.utter_message(text=" Enter Issue Summary")
            return []


class ValidateIssueCreationForm(FormValidationAction):

    def name(self) -> Text:
        return "validate_issue_creation_from"

    def validate_issue_summary(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate cuisine value."""

        if len(slot_value) < 3:
            dispatcher.utter_message(text="The Summary Is Too  Short ..")
            return {"issue_summary": None}
        elif 'cancel_form' in slot_value:
            dispatcher.utter_message(text="Canceled !!")
            return {'issue_summary': None, 'requested_slot': None}
        else:
            if tracker.get_slot("email") is None:
                return {"issue_summary": None}
            else:
                return {"issue_summary": slot_value}

    def validate_issue_description(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:

        if len(slot_value) < 5:
            dispatcher.utter_message(text="The Description Is Too  Short ..")
            return {"issue_description": None}
        elif 'cancel_form' in slot_value:
            dispatcher.utter_message(text="Canceled !!")
            return {'issue_summary': None, 'issue_description': None, 'requested_slot': None}
        else:
            return {'issue_description': slot_value}


class ActionShowIsssue(Action):

    def name(self) -> Text:
        return "action_submit_issue_creation"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        email_id = tracker.get_slot('email')
        api_key = tracker.get_slot('api_key')
        project_key = tracker.get_slot('project_key')
        issue_summary = tracker.get_slot('issue_summary')
        issue_description = tracker.get_slot('issue_description')
        url = "https://saharshsolanki1.atlassian.net//rest/api/2/issue"
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
        payload = json.dumps(
            {
                "fields": {
                    "project":
                        {
                            "key": project_key
                        },
                    "summary": issue_summary,
                    "description": issue_description,
                    "issuetype": {
                        "name": "Task"
                    }
                }
            }
        )
        response = requests.post(url, headers=headers, data=payload,
                                 auth=(email_id, api_key))
        data = response.json()

        dispatcher.utter_message(text="Issue Created Successfully !! And Issue ID Is " + data["id"])
        return [SlotSet("issue_summary", None), SlotSet("issue_description", None)]


class ValidateLoginUserFrom(FormValidationAction):

    def name(self) -> Text:
        return "validate_login_user_form"

    def validate_email(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:

        if "@" in slot_value:
            return {"email": slot_value}
        elif 'cancel_form' in slot_value:
            dispatcher.utter_message(text="Canceled !!")
            return {'email': None, 'requested_slot': None}
        else:
            dispatcher.utter_message(text="Hey !! Please Enter Correct Email")
            return {"email": None}

    def validate_api_key(
            self,
            slot_value: Any,
            dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: DomainDict,
    ) -> Dict[Text, Any]:
        """Validate cuisine value."""

        emails = tracker.get_slot('email')
        password = slot_value
        if password == "":
            dispatcher.utter_message(
                text="Api Key Is Empty !")
            return {"api_key": None}
        elif 'cancel_form' in slot_value:
            dispatcher.utter_message(text="Canceled !!")
            return {'email': None, 'password': None, 'requested_slot': None}
        else:
            dispatcher.utter_message(text="Validating")
            check = login_check(emails, password)

            if check == True:
                dispatcher.utter_message(text="Details Are Correct Now You Can Perform Certain Actions")
                return {"api_key": slot_value}
            else:
                dispatcher.utter_message(text="I Can't Verify Your Email and password")
                return {"email": None, "api_key": None}


class ActionShowProject(Action):

    def name(self) -> Text:
        return "action_show_project"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        email_id = tracker.get_slot('email')
        api_key = tracker.get_slot('api_key')
        if email_id is None:
            dispatcher.utter_message(text="I Can't Show You Projects Becase Your Are Not LoggedIn")
            dispatcher.utter_button_message(text="Want To Login ???",
                                            buttons=[{"title": "YES", 'payload': "Login"}]
                                            )
            return []
        elif api_key is None:
            dispatcher.utter_message(text="I Can't Show You Projects Becase Your Are Not LoggedIn")
            dispatcher.utter_button_message(text="Want To Login ???",
                                            buttons=[{"title": "YES", 'payload': "Login"}]
                                            )
            return []
        else:

            url = "https://saharshsolanki1.atlassian.net/rest/api/2/project"
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json"
            }
            query = {}
            response = requests.get(url, headers=headers, params=query,
                                    auth=(email_id, api_key))
            data = response.json()

            if len(data) is 0:
                dispatcher.utter_message(text="You don't have any projects ")
                dispatcher.utter_message(text="Want to create a project",buttons=[{'title':"Create project",'payload':"create project"}])
            for d in data:
                project_url = d['self']
                project_name = d['name']
                project_id = d['id']
                project_key = d['key']
                msg = f"Project Name : {project_name} \n Project Id : {project_id} \n Project Key : {project_key} "
                dispatcher.utter_message(text=msg)
            return []


class action_cancel(Action):

    def name(self) -> Text:
        return "action_cancel"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        if tracker.get_slot("requested_slot"):
            dispatcher.utter_message(text="Canceled The Process !")
            return {"requested_slot": None}
        else:
            dispatcher.utter_message(text="Nothing To Cancel !")


class action_help(Action):

    def name(self) -> Text:
        return "action_help"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        my_text = f""
        count = 1
        for data in help:
            my_text = my_text + str(count) + ") " + data['command'] + " : " + data['message'] + " " + " \n . \n "
            count = count + 1
        dispatcher.utter_message(text=my_text)
        return []


class ActionShowIsssue(Action):

    def name(self) -> Text:
        return "action_show_my_issue"

    def run(self, dispatcher: CollectingDispatcher,
            tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        email_id = tracker.get_slot('email')
        api_key = tracker.get_slot('api_key')

        if email_id is None:
            dispatcher.utter_message(text="I Can't Show You Projects Becase Your Are Not LoggedIn")
            dispatcher.utter_button_message(text="Want To Login ???",
                                            buttons=[{"title": "YES", 'payload': "Login"}]
                                            )
            return []
        elif api_key is None:
            dispatcher.utter_message(text="I Can't Show You Projects Becase Your Are Not LoggedIn")
            dispatcher.utter_button_message(text="Want To Login ???",
                                            buttons=[{"title": "YES", 'payload': "Login"}]
                                            )
            return []
        elif tracker.get_slot("project_key") is None:
            dispatcher.utter_message(
                text="I Don't Know In Which Projects Issue I Should Show !! You Can Set It By Set My Project")
            dispatcher.utter_button_message(text="Want To Set Current Project Key ???",
                                            buttons=[{"title": "YES", 'payload': "Set Working Project Key"}]
                                            )
            return []
        else:
            url = "https://saharshsolanki1.atlassian.net/rest/api/3/search"
            headers = {
                "Accept": "application/json",
                "Content-Type": "application/json"
            }

            query = {
                'jql': 'project = ' + tracker.get_slot("project_key")
            }

            response = requests.get(url, headers=headers, params=query,
                                    auth=(email_id, api_key))
            data = response.json()

            issues = data["issues"]
            if len(issues) is 0:
                dispatcher.utter_message('no issue available in your project')
            for issue in issues:
                try:
                    issue_title = issue['fields']['summary']
                    issue_text = issue['fields']['description']['content'][0]['content'][0]['text']
                    issue_by = issue['fields']['reporter']['displayName']
                    issue_name = issue['fields']['status']['statusCategory']['name']
                    issue_id = issue['id']
                    issue_key = issue['key']
                    msg = f"Issue Title : {issue_title} \n Issue Description : {issue_text} \n Issue In   : {issue_name} \n Issue Id {issue_id} \n Issue KEY {issue_key} "
                    dispatcher.utter_message(text=msg)
                except:
                    issue_id = issue['id']
                    dispatcher.utter_message(text="I Got Error While Loading This Issue ID :" + issue_id)
            return []
