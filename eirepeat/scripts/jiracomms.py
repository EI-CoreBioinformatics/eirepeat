#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Script to post to jira
"""

# authorship
__author__ = "Gemy George Kaithakottil"
__maintainer__ = "Gemy George Kaithakottil"
__email__ = "gemygk@gmail.com"

# import libraries
import sys
import os
import requests
from requests.auth import HTTPBasicAuth
import json

# Header for HTTP request, make sure it knows a JSON object is coming
head = {"Content-type": "application/json"}

# JIRA wasn't originally designed to store fields specifically relating to sequencing, so these are set via custom fields
# CUSTOM_FIELD = {
#     "platform": "customfield_10410",
#     "instrument": "customfield_10528",
#     "chemistry": "customfield_11010",
#     "custom_primers": "customfield_10522",
#     "read_config": "customfield_10411"
# }

CUSTOM_FIELD = {"pip": "customfield_11012", "pipeline": "customfield_11226"}


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

    @staticmethod
    def get_ticket(jira_id):
        # The URL to JIRA using JQL.  Custom field 10410 refers to the platform field and 10528 refers to the instrument field.
        url = (
            JiraInfo.SITE
            + "/rest/api/latest/search?jql=key="
            + jira_id
            + "&fields=summary,"
            + ",".join(list(CUSTOM_FIELD.values()))
        )

        # Get the data from jira
        response = requests.get(url, headers=head, auth=JiraInfo.CREDENTIALS)
        if not response.ok:
            raise ValueError(
                "Error retrieving JIRA ticket "
                + jira_id
                + "\nResponse code: "
                + str(response.status_code)
                + "\nReason: "
                + response.reason
            )
        return None

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

        # The payload to submit as a python dictionary
        payload = {"body": content}

        # Convert payload from a python dictionary to json object
        data = json.dumps(payload)

        # Hardcoded path to JIRA, appended with the ticket id
        url = JiraInfo.SITE + "/rest/api/latest/issue/" + str(self.jira) + "/comment"

        # Post the payload to jira
        ret = requests.post(url, data, headers=head, auth=JiraInfo.CREDENTIALS)

        # Check the response indicated a success
        return ret.ok

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
            type = "text/csv"
        elif ext == ".html":
            type = "text/html"
        elif ext == ".htm":
            type = "text/html"
        elif ext == ".txt":
            type = "text/plain"
        elif ext == ".pdf":
            type = "application/pdf"
        elif ext == ".xls" or ext == ".xlsx":
            type = "application/vnd.ms-excel"
        else:
            raise ValueError("File has an unsupported extension: " + file_to_attach)

        file = {
            "file": (
                name if name and name != "" else os.path.basename(file_to_attach),
                open(file_to_attach, "rb"),
                type,
            )
        }

        header = {"X-Atlassian-Token": "nocheck"}

        # Hardcoded path to JIRA, appended with the ticket id
        url = (
            JiraInfo.SITE + "/rest/api/latest/issue/" + str(self.jira) + "/attachments"
        )

        # Post the payload to jira
        ret = requests.post(url, headers=header, auth=JiraInfo.CREDENTIALS, files=file)

        # Check the response indicated a success
        if ret.ok:
            content = json.loads(ret.text)

            # If that went well, then if we also have a comment add that to the ticket too
            message = ""
            if prefix and prefix.strip() != "":
                message = (
                    prefix.strip()
                    + ": ["
                    + content[0]["filename"]
                    + "|"
                    + content[0]["content"]
                    + "]"
                )

            if suffix and suffix.strip() != "":
                message += "\n\n" + suffix

            if message != "":
                return self.post_comment(message)

        return ret.ok


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
    # return JiraInfo.get_ticket(jira_id).post_comment(comment)
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
    # return JiraInfo.get_ticket(jira_id).post_attachment(prefix, file_to_attach, name if name and name != "" else os.path.basename(file_to_attach), suffix)
    return JiraInfo(jira_id).post_attachment(
        prefix,
        file_to_attach,
        name if name and name != "" else os.path.basename(file_to_attach),
        suffix,
    )

