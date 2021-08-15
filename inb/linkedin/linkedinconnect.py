# MIT License
#
# Copyright (c) 2019 Creative Commons
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS
# OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

"""from __future__ imports must occur at the beginning of the file. DO NOT CHANGE!"""
from __future__ import annotations

import time

from .person import Person
from .DOM.cleaners import Cleaner
from .invitation.status import Invitation

from errors import EmptyResponseException
from errors import ConnectionLimitExceededException

from selenium import webdriver

from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import ElementNotInteractableException
from selenium.common.exceptions import ElementClickInterceptedException

from selenium.webdriver.common.action_chains import ActionChains


class LinkedInConnectionsAuto(object):
    __INVITATION_SENT: int = 0

    def __init__(
        self: LinkedInConnectionsAuto,
        driver: webdriver.Chrome,
        limit: int = 40
    ) -> None:
        """LinkedInConnectionsAuto class constructor to initialise LinkedInConnectionsAuto object.

        :Args:
            - self: {LinkedInConnectionsAuto} object
            - _linkedin: {LinkedIn} LinkedIn class object to access the driver object
            - limit: {int} daily invitation limit

        :Returns:
            - {LinkedInConnectionsAuto} LinkedInConnectionsAuto object

        :Raises:
            - PropertyNotExistException if object _linkedin doesn't have a property driver in it
            - ConnectionLimitExceededException if user gives a connection limit that exceeds 80

        :Usage:
            - _linkedin_connection_auto = LinkedInConnectionAuto(_linkedin, 40)
        """
        if not isinstance(driver, webdriver.Chrome):
            raise Exception(
                "Object '%(driver)s' is not a 'webdriver.Chrome' object!" % {
                    "driver": type(driver)})

        self._driver = driver

        if limit > 80:
            raise ConnectionLimitExceededException(
                "Daily invitation limit can't be greater than 80, we recommend 40!")

        self._limit = limit

    def get_my_network(
        self: LinkedInConnectionsAuto,
        _url: str = "https://www.linkedin.com/mynetwork/"
    ) -> None:
        """Method get_my_network() sends a GET request to the network page of LinkedIn.

        :Args:
            - self: {LinkedInConnectionsAuto} object
            - _url: {str} url to send GET request to

        :Returns:
            - {None}

        :Raises:
            - EmptyResponseException if there is a TimeoutException

        :Usage:
            - _linkedin_connections_auto.get_my_network("https://www.linkedin.com/mynetwork/")
        """
        try:
            self._driver.get(_url)
        except TimeoutException:
            raise EmptyResponseException("ERR_EMPTY_RESPONSE")

    def send_invitation(self: LinkedInConnectionsAuto) -> None:
        """Method send_invitation() starts sending invitation to people on linkedin.

        :Args:
            - self: {LinkedInConnectionsAuto} object

        :Returns:
            - {None}
        """
        _start = time.time()

        _p = Person(self._driver)
        _person = _p.get_suggestion_box_element()

        while _person:
            if LinkedInConnectionsAuto.__INVITATION_SENT == self._limit:
                break

            if not _person._connect_button.find_element_by_tag_name("span").text == "Connect":
                continue

            try:
                ActionChains(self._driver).move_to_element(
                    _person._connect_button).click().perform()
                Invitation(name=_person._name,
                           occupation=_person._occupation,
                           status="sent",
                           elapsed_time=time.time() - _start).status()
                LinkedInConnectionsAuto.__INVITATION_SENT += 1
            except (ElementNotInteractableException, ElementClickInterceptedException) as error:
                if isinstance(error, ElementClickInterceptedException):
                    break
                Invitation(name=_person._name,
                           occupation=_person._occupation,
                           status="failed",
                           elapsed_time=time.time() - _start).status()

            _person = _p.get_suggestion_box_element()

    def execute_cleaners(self: LinkedInConnectionsAuto) -> None:
        """Method execute_cleaners() scours the unwanted element from the page during the
        connect process.

        :Args:
            - self: {LinkedInConnectionsAuto}
        """
        Cleaner(self._driver).clear_message_overlay()

    def run(self: LinkedInConnectionsAuto) -> None:
        """Method run() calls the send_invitation method, but first it assures that the object
        self has driver property in it.

        :Args:
            - self: {LinkedInConnectionsAuto} object

        :Returns:
            - {None}
        """
        self.execute_cleaners()

        self.send_invitation()

    def __del__(self: LinkedInConnectionsAuto) -> None:
        """LinkedInConnectionsAuto destructor to de-initialise LinkedInConnectionsAuto object.

        :Args:
            - self: {LinkedInConnectionsAuto} object

        :Returns:
            - {None}
        """
        LinkedInConnectionsAuto.__INVITATION_SENT = 0

        if isinstance(self._driver, webdriver.Chrome):
            self._driver.quit()