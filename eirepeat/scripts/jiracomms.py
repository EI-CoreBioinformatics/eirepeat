#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script to post to jira
"""

# import libraries
import os
import requests
from requests.auth import HTTPBasicAuth
import json

# Header for HTTP request, make sure it knows a JSON object is coming
head = {"Content-type": "application/json"}


class JiraInfo:
    # Base address for JIRA
    SITE = None
    CREDENTIALS = None

    def __init__(self, jira):
        self.jira = jira

    @staticmethod
    def initialise(
        pap_config=None, jira_site=None, jira_username=None, jira_password=None
    ):
        if pap_config:
            if not jira_password:
                with open(pap_config["jira"]["password_file"], "r") as passfile:
                    jira_password = passfile.read().replace("\n", "")
            JiraInfo.SITE = jira_site if jira_site else pap_config["jira"]["site"]
            JiraInfo.CREDENTIALS = HTTPBasicAuth(
                jira_username if jira_username else pap_config["jira"]["username"],
                jira_password,
            )
        else:
            JiraInfo.SITE = JiraInfo.CREDENTIALS = None

    def post_comment(self, comment):
        """
        This method posts a payload to this jira ticket as a comment
        :param comment: The comment to post.  If the comment is a path that points to a file that exists then this file is
        loaded and the contents used as the payload.
        :return: True if message posted correctly, false otherwise
        """

        content = ""

        # If comment is a path, check if a file exists at that path, and if so load the contents of the file,
        # otherwise just use the comment as the content for the json payload
        if os.path.exists(comment):
            with open(comment, "r") as content_file:
                content = content_file.read().replace("\r", "")
        else:
            content = comment

        # headers for posting comment
        headers = {"Accept": "application/json", "Content-Type": "application/json"}

        # The payload to submit as a python dictionary
        # Convert payload from a python dictionary to json object
        payload = json.dumps(
            {
                "body": {
                    "type": "doc",
                    "version": 1,
                    "content": [
                        {
                            "type": "paragraph",
                            "content": [{"text": content, "type": "text"}],
                        }
                    ],
                },
            }
        )

        # Hardcoded path to JIRA, appended with the ticket id
        url = JiraInfo.SITE + "/rest/api/3/issue/" + str(self.jira) + "/comment"

        # Post the payload to jira
        response = requests.request(
            "POST", url, data=payload, headers=headers, auth=JiraInfo.CREDENTIALS
        )

        # Capture JIRA Cloud API response
        print_jira_api_response(response)

        # Check the response indicated a success
        return response.ok

    def post_attachment(self, prefix, file_to_attach, name, suffix=None):
        """
        This method will attach a file to this jira ticket
        :param prefix: The comment to post.  If the comment is a path that points to a file that exists then this file is
        loaded and the contents used as the payload
        :param file_to_attach: The file to attach to the jira ticket
        :param name: The name for the file in JIRA (by default will be the filename of file_to_attach)
        :param suffix: Additional content to go after the original message
        :return: True if message posted correctly, false otherwise
        """

        # If comment is a path, check if a file exists at that path, and if so load the contents of the file,
        # otherwise just use the comment as the content for the json payload
        if not os.path.exists(file_to_attach):
            raise ValueError(
                'File "'
                + file_to_attach
                + "\" could not be found and therefore can't be attached to JIRA ticket "
                + self.jira
            )

        filename, ext = os.path.splitext(file_to_attach)

        if ext == ".csv":
            filetype = "text/csv"
        elif ext == ".html":
            filetype = "text/html"
        elif ext == ".htm":
            filetype = "text/html"
        elif ext == ".txt":
            filetype = "text/plain"
        elif ext == ".pdf":
            filetype = "application/pdf"
        elif ext == ".xls" or ext == ".xlsx":
            filetype = "application/vnd.ms-excel"
        else:
            raise ValueError("File has an unsupported extension: " + file_to_attach)

        files = {
            "file": (
                name if name and name != "" else os.path.basename(file_to_attach),
                open(file_to_attach, "rb"),
                filetype,
            )
        }

        header = {"Accept": "application/json", "X-Atlassian-Token": "nocheck"}

        # Hardcoded path to JIRA, appended with the ticket id
        url = JiraInfo.SITE + "/rest/api/3/issue/" + str(self.jira) + "/attachments"

        # Post the payload to jira
        response = requests.request(
            "POST", url, headers=header, auth=JiraInfo.CREDENTIALS, files=files
        )

        # Capture JIRA Cloud API response
        print_jira_api_response(response)

        # Check the response indicated a success
        if response.ok:
            content = json.loads(response.text)
            attached_file_name = content[0]["filename"]
            attached_file_link = content[0]["content"]

            # add header comment
            comment_headers = {
                "Accept": "application/json",
                "Content-Type": "application/json",
            }
            url = JiraInfo.SITE + "/rest/api/3/issue/" + str(self.jira) + "/comment"

            # If that went well, then if we also have a comment add that to the ticket too
            if prefix and prefix.strip() == "":
                prefix = " "
            if suffix and suffix.strip() == "":
                suffix = " "

            payload = json.dumps(
                {
                    "body": {
                        "version": 1,
                        "type": "doc",
                        "content": [
                            {
                                "type": "paragraph",
                                "content": [
                                    {"type": "text", "text": prefix if prefix else " "},
                                    {
                                        "type": "text",
                                        "text": attached_file_name,
                                        "marks": [
                                            {
                                                "type": "link",
                                                "attrs": {"href": attached_file_link},
                                            }
                                        ],
                                    },
                                    {"type": "text", "text": suffix if suffix else " "},
                                ],
                            }
                        ],
                    },
                }
            )

            # Post the payload to jira
            response = requests.request(
                "POST",
                url,
                data=payload,
                headers=comment_headers,
                auth=JiraInfo.CREDENTIALS,
            )

            # Capture JIRA Cloud API response
            print_jira_api_response(response)

        return response.ok

def post_to_jira(jira_id, comment, jira_config=None):
    """
    This method posts a payload to a jira ticket as a comment
    :param jira_id: The issue/ticket id
    :param comment: The comment to post.  If the comment is a path that points to a file that exists then this file is
    loaded and the contents used as the payload
    :return: True if message posted correctly, false otherwise
    """
    if jira_config:
        JiraInfo.initialise(pap_config=jira_config)
    return JiraInfo(jira_id).post_comment(comment)


def post_attachment_to_jira(
    jira_id, prefix, file_to_attach, name=None, suffix=None, jira_config=None
):
    """
    This method posts a payload to a jira ticket as a comment
    :param jira_id: The issue/ticket id
    :param prefix: The comment to post, alongside the attachement
    :param file_to_attach: The attachment to add to the ticket
    :param name: Filename for JIRA (by default will be same as file_to_attach)
    :param suffix: Additional content to go after the original message.
    :return: True if message posted correctly, false otherwise
    """
    if jira_config:
        JiraInfo.initialise(pap_config=jira_config)
    return JiraInfo(jira_id).post_attachment(
        prefix,
        file_to_attach,
        name if name and name != "" else os.path.basename(file_to_attach),
        suffix,
    )

def print_jira_api_response(response):
    """
    Returns the JIRA Clould API response directory associated withy the given JIRA ticket
    :param response: Requests return response
    """
    print(
        json.dumps(
            json.loads(response.text), sort_keys=True, indent=4, separators=(",", ": ")
        )
    )
