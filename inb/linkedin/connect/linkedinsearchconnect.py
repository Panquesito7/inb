# pylint: disable=missing-module-docstring

# Copyright 2021, joshiayus Inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are
# met:
#
#     * Redistributions of source code must retain the above copyright
# notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above
# copyright notice, this list of conditions and the following disclaimer
# in the documentation and/or other materials provided with the
# distribution.
#     * Neither the name of joshiayus Inc. nor the names of its
# contributors may be used to endorse or promote products derived from
# this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR
# A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT
# OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL,
# SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE,
# DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY
# THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

from __future__ import annotations

import re
import sys
import time
import logging
import traceback

from typing import (Optional, Union)

from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.remote import webelement
from selenium.webdriver.common import (
    by,
    keys,
    action_chains,
)
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from linkedin import (driver, settings, connect)
from linkedin.document_object_module import javascript
from linkedin.message import template
from linkedin.connect import (pathselectorbuilder, utils)
from linkedin.invitation import status

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

file_handler = logging.FileHandler(settings.LOG_DIR_PATH / __name__, mode='a')
file_handler.setFormatter(logging.Formatter(settings.LOG_FORMAT_STR))

if settings.LOGGING_TO_STREAM_ENABLED:
  stream_handler = logging.StreamHandler(sys.stderr)
  stream_handler.setFormatter(logging.Formatter(settings.LOG_FORMAT_STR))
  logger.addHandler(stream_handler)

logger.addHandler(file_handler)


class _SearchResultsPageElementsPathSelectors:
  """Serves elements' path selectors needed for scraping users information from
  the search results page.
  """

  @staticmethod
  def get_global_nav_typeahead_input_box_xpath(
  ) -> pathselectorbuilder.PathSelectorBuilder:
    """Returns the path selector for the global nav typeahead input box.

    Returns:
      The path selector for the global nav typeahead input box and its label.
    """
    return pathselectorbuilder.PathSelectorBuilder(
        'Global <nav> typeahead input box',
        '//*[@id="global-nav-typeahead"]/input')

  @staticmethod
  def get_filter_by_people_button_xpath(
  ) -> pathselectorbuilder.PathSelectorBuilder:
    """Returns the path selector for the filter by people button.

    Returns:
      The path selector for the filter by people button and its label.
    """
    return pathselectorbuilder.PathSelectorBuilder(
        'Filter by people button',
        '//div[@id="search-reusables__filters-bar"]//button[@aria-label="People"]'  # pylint: disable=line-too-long
    )

  @staticmethod
  def get_all_filters_button_xpath() -> pathselectorbuilder.PathSelectorBuilder:
    """Returns the path selector for the all filters button.

    Returns:
      The path selector for the all filters button and its label.
    """
    return pathselectorbuilder.PathSelectorBuilder(
        'All filters button',
        '//div[@id="search-reusables__filters-bar"]//button[starts-with(@aria-label, "Show all filters.")]'  # pylint: disable=line-too-long
    )

  @staticmethod
  def get_available_location_options_xpath(
  ) -> pathselectorbuilder.PathSelectorBuilder:
    """Returns the path selector for the available location options.

    Returns:
      The path selector for the available location options and its label.
    """
    return pathselectorbuilder.PathSelectorBuilder(
        'Available location options',
        '//input[starts-with(@id, "advanced-filter-geoUrn-")]')

  @staticmethod
  def get_available_location_labels_xpath(
  ) -> pathselectorbuilder.PathSelectorBuilder:
    """Returns the path selector for the available location labels.

    Returns:
      The path selector for the available location labels and its label.
    """
    return pathselectorbuilder.PathSelectorBuilder(
        'Available location labels',
        '//label[starts-with(@for, "advanced-filter-geoUrn-")]')

  @staticmethod
  def get_available_industry_options_xpath(
  ) -> pathselectorbuilder.PathSelectorBuilder:
    """Returns the path selector for the available industry options.

    Returns:
      The path selector for the available industry options and its label.
    """
    return pathselectorbuilder.PathSelectorBuilder(
        'Available industry options',
        '//input[starts-with(@id, "advanced-filter-industry-")]')

  @staticmethod
  def get_available_industry_labels_xpath(
  ) -> pathselectorbuilder.PathSelectorBuilder:
    """Returns the path selector for the available industry labels.

    Returns:
      The path selector for the available industry labels and its label.
    """
    return pathselectorbuilder.PathSelectorBuilder(
        'Available industry labels',
        '//label[starts-with(@for, "advanced-filter-industry-")]')

  @staticmethod
  def get_available_profile_language_options_xpath(
  ) -> pathselectorbuilder.PathSelectorBuilder:
    """Returns the path selector for the available profile language options.

    Returns:
      The path selector for the available profile language options and its
      label.
    """
    return pathselectorbuilder.PathSelectorBuilder(
        'Available profile language options',
        '//input[starts-with(@id, "advanced-filter-profileLanguage-")]')

  @staticmethod
  def get_available_profile_langauge_labels_xpath(
  ) -> pathselectorbuilder.PathSelectorBuilder:
    """Returns the path selector for the available profile language labels.

    Returns:
      The path selector for the available profile language labels and its
      label.
    """
    return pathselectorbuilder.PathSelectorBuilder(
        'Available profile language labels',
        '//label[starts-with(@for, "advanced-filter-profileLanguage-")]')

  @staticmethod
  def get_first_name_input_element_container_xpath(
  ) -> pathselectorbuilder.PathSelectorBuilder:
    """Returns the path selector for the first name input element container.

    Returns:
      The path selector for the first name input element container and its
      label.
    """
    return pathselectorbuilder.PathSelectorBuilder(
        'First name <input> element container',
        '//label[contains(text(), "First name")]')

  @staticmethod
  def get_last_name_input_element_container_xpath(
  ) -> pathselectorbuilder.PathSelectorBuilder:
    """Returns the path selector for the last name input element container.

    Returns:
      The path selector for the last name input element container and its
      label.
    """
    return pathselectorbuilder.PathSelectorBuilder(
        'Last name <input> element container',
        '//label[contains(text(), "Last name")]')

  @staticmethod
  def get_title_input_element_container_xpath(
  ) -> pathselectorbuilder.PathSelectorBuilder:
    """Returns the path selector for the title input element container.

    Returns:
      The path selector for the title input element container and its label.
    """
    return pathselectorbuilder.PathSelectorBuilder(
        'Title <input> element container', '//label[contains(text(), "Title")]')

  @staticmethod
  def get_current_company_input_element_container_xpath(
  ) -> pathselectorbuilder.PathSelectorBuilder:
    """Returns the path selector for the current company input element
    container.

    Returns:
      The path selector for the current company input element container and
      its label.
    """
    return pathselectorbuilder.PathSelectorBuilder(
        'Current company <input> element container',
        '//label[contains(text(), "Company")]')

  @staticmethod
  def get_school_input_element_container_xpath(
  ) -> pathselectorbuilder.PathSelectorBuilder:
    """Returns the path selector for the school input element container.

    Returns:
      The path selector for the school input element container and its label.
    """
    return pathselectorbuilder.PathSelectorBuilder(
        'School <input> element container',
        '//label[contains(text(), "School")]')

  @staticmethod
  def get_apply_current_filters_button_xpath(
  ) -> pathselectorbuilder.PathSelectorBuilder:
    """Returns the path selector for the apply current filters button.

    Returns:
      The path selector for the apply current filters button and its label.
    """
    return pathselectorbuilder.PathSelectorBuilder(
        'Apply current filters <button>',
        '//div[@id="artdeco-modal-outlet"]//button[@aria-label="Apply current filters to show results"]'  # pylint: disable=line-too-long
    )

  @staticmethod
  def get_search_results_person_li_parent_xpath(
  ) -> pathselectorbuilder.PathSelectorBuilder:
    """Returns the path selector for the search results person li parent.

    Returns:
      The path selector for the search results person li parent and its
      label.
    """
    return pathselectorbuilder.PathSelectorBuilder(
        'Search results person <li> parent',
        '//*[@id="main"]/div/div/div[1]/ul')

  @staticmethod
  def get_search_results_person_li_xpath(
      positiion: int) -> pathselectorbuilder.PathSelectorBuilder:
    """Returns the path selector for the search results person li.

    Args:
      position: `li` position.

    Returns:
      The path selector for the search results person li and its label.
    """
    return pathselectorbuilder.PathSelectorBuilder(
        'Search results person <li>',
        f'{_SearchResultsPageElementsPathSelectors.get_search_results_person_li_parent_xpath()}/li[{positiion}]'  # pylint: disable=line-too-long
    )

  @staticmethod
  def _get_search_results_person_li_card_container_xpath(
      position: int) -> pathselectorbuilder.PathSelectorBuilder:
    """Returns the path selector for the search results person li card
    container.

    Args:
      position: `li` position.

    Returns:
      The path selector for the search results person li card container and
      its label.
    """
    return pathselectorbuilder.PathSelectorBuilder(
        'Search results person <li> card container',
        f'{_SearchResultsPageElementsPathSelectors.get_search_results_person_li_xpath(position)}/div/div'  # pylint: disable=line-too-long
    )

  @staticmethod
  def _get_search_results_person_li_card_info_container_xpath(
      position: int) -> pathselectorbuilder.PathSelectorBuilder:
    """Returns the path selector for the search results person li card
    info container.

    Args:
      position: `li` position.

    Returns:
      The path selector for the search results person li card info container
      and its label.
    """
    return pathselectorbuilder.PathSelectorBuilder(
        'Search results person <li> card info container',
        f'{_SearchResultsPageElementsPathSelectors._get_search_results_person_li_card_container_xpath(position)}/div[2]'  # pylint: disable=line-too-long
    )

  @staticmethod
  def _get_search_results_person_li_card_info_nav_xpath(
      position: int) -> pathselectorbuilder.PathSelectorBuilder:
    """Returns the path selector for the search results person li card
    info nav.

    Args:
      position: `li` position.

    Returns:
      The path selector for the search results person li card info nav and
      its label.
    """
    return pathselectorbuilder.PathSelectorBuilder(
        'Search results person <li> card info <nav>',
        f'{_SearchResultsPageElementsPathSelectors._get_search_results_person_li_card_info_container_xpath(position)}/div[1]/div[1]/div'  # pylint: disable=line-too-long
    )

  @staticmethod
  def _get_search_results_person_li_card_info_footer_xpath(
      position: int) -> pathselectorbuilder.PathSelectorBuilder:
    """Returns the path selector for the search results person li card
    info footer.

    Args:
      position: `li` position.

    Returns:
      The path selector for the search results person li card info footer
      and its label.
    """
    return pathselectorbuilder.PathSelectorBuilder(
        'Search results person <li> card info <footer>',
        f'{_SearchResultsPageElementsPathSelectors._get_search_results_person_li_card_info_container_xpath(position)}/div[3]'  # pylint: disable=line-too-long
    )

  @staticmethod
  def get_search_results_person_li_card_mutual_connections_info_container_xpath(
      position: int) -> pathselectorbuilder.PathSelectorBuilder:
    """Returns the path selector for the search results person li card
    mutual connections info container.

    Args:
      position: `li` position.

    Returns:
      The path selector for the search results person li card mutual
      connections info container and its label.
    """
    return pathselectorbuilder.PathSelectorBuilder(
        'Search results person <li> card mutual connections info container',
        f'{_SearchResultsPageElementsPathSelectors._get_search_results_person_li_card_info_footer_xpath(position)}/div/div[2]/span'  # pylint: disable=line-too-long
    )

  @staticmethod
  def get_search_results_person_li_card_link_xpath(
      position: int) -> pathselectorbuilder.PathSelectorBuilder:
    """Returns the path selector for the search results person li card
    link.

    Args:
      position: `li` position.

    Returns:
      The path selector for the search results person li card link and
      its label.
    """
    return pathselectorbuilder.PathSelectorBuilder(
        'Search results person <li> card link',
        f'{_SearchResultsPageElementsPathSelectors._get_search_results_person_li_card_info_nav_xpath(position)}/span[1]/span/a'  # pylint: disable=line-too-long
    )

  @staticmethod
  def get_search_results_person_li_card_name_xpath(
      position: int) -> pathselectorbuilder.PathSelectorBuilder:
    """Returns the path selector for the search results person li card
    name.

    Args:
      position: `li` position.

    Returns:
      The path selector for the search results person li card name and
      its label.
    """
    return pathselectorbuilder.PathSelectorBuilder(
        'Search results person <li> card name',
        f'{_SearchResultsPageElementsPathSelectors._get_search_results_person_li_card_info_nav_xpath(position)}/span[1]/span/a/span/span[1]'  # pylint: disable=line-too-long
    )

  @staticmethod
  def get_search_results_person_li_card_degree_info_xpath(
      position: int) -> pathselectorbuilder.PathSelectorBuilder:
    """Returns the path selector for the search results person li card
    degree info.

    Args:
      position: `li` position.

    Returns:
      The path selector for the search results person li card degree info
      and its label.
    """
    return pathselectorbuilder.PathSelectorBuilder(
        'Search results person <li> card degree info',
        f'{_SearchResultsPageElementsPathSelectors._get_search_results_person_li_card_info_nav_xpath(position)}/span[2]/div/span/span[2]'  # pylint: disable=line-too-long
    )

  @staticmethod
  def _get_search_results_person_li_occupation_and_location_info_card_container_xpath(  # pylint: disable=line-too-long
      position: int) -> pathselectorbuilder.PathSelectorBuilder:
    """Returns the path selector for the search results person li occupation
    and location info card container.

    Args:
      position: `li` position.

    Returns:
      The path selector for the search results person li occupation and
      location info card container and its label.
    """
    return pathselectorbuilder.PathSelectorBuilder(
        'Search results person <li> occupation and location info card container',
        f'{_SearchResultsPageElementsPathSelectors._get_search_results_person_li_card_info_container_xpath(position)}/div[1]/div[2]'  # pylint: disable=line-too-long
    )

  @staticmethod
  def get_search_results_person_li_occupation_info_card_container_xpath(
      position: int) -> pathselectorbuilder.PathSelectorBuilder:
    """Returns the path selector for the search results person li occupation
    info card container.

    Args:
      position: `li` position.

    Returns:
      The path selector for the search results person li occupation info
      card container and its label.
    """
    return pathselectorbuilder.PathSelectorBuilder(
        'Search results person <li> occupation info card container',
        f'{_SearchResultsPageElementsPathSelectors._get_search_results_person_li_occupation_and_location_info_card_container_xpath(position)}/div/div[1]'  # pylint: disable=line-too-long
    )

  @staticmethod
  def get_search_results_person_li_location_info_card_container_xpath(
      position: int) -> pathselectorbuilder.PathSelectorBuilder:
    """Returns the path selector for the search results person li location
    info card container.

    Args:
      position: `li` position.

    Returns:
      The path selector for the search results person li location info
      card container and its label.
    """
    return pathselectorbuilder.PathSelectorBuilder(
        'Search results person <li> location info card container',
        f'{_SearchResultsPageElementsPathSelectors._get_search_results_person_li_occupation_and_location_info_card_container_xpath(position)}/div/div[2]'  # pylint: disable=line-too-long
    )

  @staticmethod
  def _get_search_results_person_li_card_actions_container_xpath(
      position: int) -> pathselectorbuilder.PathSelectorBuilder:
    """Returns the path selector for the search results person li card
    actions container.

    Args:
      position: `li` position.

    Returns:
      The path selector for the search results person li card actions
      container and its label.
    """
    return pathselectorbuilder.PathSelectorBuilder(
        'Search results person <li> card actions container',
        f'{_SearchResultsPageElementsPathSelectors._get_search_results_person_li_card_container_xpath(position)}/div[3]/div'  # pylint: disable=line-too-long
    )

  @staticmethod
  def get_search_results_person_li_connect_button_xpath(
      position: int) -> pathselectorbuilder.PathSelectorBuilder:
    """Returns the path selector for the search results person li connect
    button.

    Args:
      position: `li` position.

    Returns:
      The path selector for the search results person li connect button
      and its label.
    """
    return pathselectorbuilder.PathSelectorBuilder(
        'Search results person <li> connect button',
        f'{_SearchResultsPageElementsPathSelectors._get_search_results_person_li_card_actions_container_xpath(position)}/button'  # pylint: disable=line-too-long
    )

  @staticmethod
  def get_send_invite_modal_xpath() -> pathselectorbuilder.PathSelectorBuilder:
    """Returns the path selector for the send invite modal.

    Returns:
      The path selector for the send invite modal and its label.
    """
    return pathselectorbuilder.PathSelectorBuilder(
        'Send invite modal', '//div[@aria-labelledby="send-invite-modal"]')

  @staticmethod
  def get_send_now_button_xpath() -> pathselectorbuilder.PathSelectorBuilder:
    """Returns the path selector for the send now button.

    Returns:
      The path selector for the send now button and its label.
    """
    return pathselectorbuilder.PathSelectorBuilder(
        'Send now <button>', '//button[@aria-label="Send now"]')

  @staticmethod
  def get_goto_next_page_button_xpath(
  ) -> pathselectorbuilder.PathSelectorBuilder:
    """Returns the path selector for the goto next page button.

    Returns:
      The path selector for the goto next page button and its label.
    """
    return pathselectorbuilder.PathSelectorBuilder(
        'Goto next page <button>',
        '//main[@id="main"]//button[@aria-label="Next"]')


class _Person:
  """A separate type for the LinkedIn user inside our program particularly
  aimed for the `LinkedInSearchConnect` API.

  Used inside the protected function `_GetSearchResultsPersonLiObject()`
  after storing the person information from the `document_object_module` inside
  the local variables like you can see below:

  ```python
  def _GetSearchResultsPersonLiObject() -> _Person:
    ...
    yield _Person(name, degree, occupation, location, mutual_connections,
                  _Person.extract_profileid_from_profileurl(profileurl),
                  profileurl, connect_button)
  ```
  """

  def __init__(self, name: str, degree: str, occupation: str, location: str,
               mutual_connections: str, profileid: str, profileurl: str,
               connect_button: webelement.WebElement):
    """Initialize a `_Person` instance.

    This helps in encapsulating data in one single entity to later use it for
    log records of a user using `inb`.

    Args:
      name: Name of the person.
      degree: The connection degree that person holds with you.
      occupation: The occupation of the person.
      location: The location of the person.
      mutual_connections: The number of mutual connections that person has.
      profileid: The profile ID of the person.
      profileurl: The profile URL of the person.
      connect_button: The web element connect button of the person.
    """
    self.name = name
    self.degree = degree
    self.occupation = occupation
    self.location = location
    self.mutual_connections = mutual_connections

    # profileid should not be dumped into the console rather it should be put
    # inside the log records i.e., our history database.
    self.profileid = profileid

    # profileurl should not be dumped into the console rather it should be put
    # inside the log records i.e., our history database.
    self.profileurl = profileurl
    self.connect_button = connect_button

  @staticmethod
  def extract_profileid_from_profileurl(profileurl: str) -> str:
    """Extracts the profile ID from the profile URL.

    Args:
      profileurl: The profile URL of the person.

    Returns:
      The profile ID of the person.
    """
    # The profile URL of the person looks like this:
    # https://www.linkedin.com/in/<profileid>/
    # So we need to extract the profile ID from the profile URL.
    re_ = re.compile(r'([a-z]+-?)+([a-zA-Z0-9]+)?', re.IGNORECASE)
    return re_.search(profileurl).group(0)


def _GetLiElementsFromPage(wait: int = 10) -> list[webelement.WebElement]:  # pylint: disable=invalid-name
  """Returns the list of `li` elements from the current page.

  Args:
    wait: The number of seconds to wait for the `li` elements to load.

  Returns:
    The list of `li` elements from the current page.
  """
  return utils.GetElementByXPath(
      _SearchResultsPageElementsPathSelectors.
      get_search_results_person_li_parent_xpath(),
      wait).find_elements_by_tag_name('li')


def _GetSearchResultsPersonLiObject() -> _Person:  # pylint: disable=invalid-name
  """Yields the `_Person` object for each person in the search results.

  This function yields the `_Person` object for each person in the search
  results while also keeping track of the page number and the page offset
  using functions such as `load_page()` and `goto_next_page()`.

  This function stops yielding as soon as the counter `person_li_count`
  reaches `connect.LINKEDIN_MAX_INVITATION_LIMIT` because that's a limit
  of connections a non-premium account can send.

  Yields:
    The `_Person` object for each person in the search results.
  """
  # The counter for the number of `li` elements in the search results.
  person_li_count = 0
  while True:
    # Get the `li` number and start scraping the data from the `li` elements
    # numberwise.
    for i in range(len(_GetLiElementsFromPage())):
      name = utils.GetElementByXPath(
          _SearchResultsPageElementsPathSelectors.
          get_search_results_person_li_card_name_xpath(i + 1)).text
      degree = utils.GetElementByXPath(
          _SearchResultsPageElementsPathSelectors.
          get_search_results_person_li_card_degree_info_xpath(i + 1)).text
      occupation = utils.GetElementByXPath(
          _SearchResultsPageElementsPathSelectors.
          get_search_results_person_li_occupation_info_card_container_xpath(
              i + 1)).text
      location = utils.GetElementByXPath(
          _SearchResultsPageElementsPathSelectors.
          get_search_results_person_li_location_info_card_container_xpath(
              i + 1)).text

      # @TODO(joshiayush): Some users on LinkedIn does not have information of
      # shared connections in the mutual connections info xpath.  To comabt this
      # exception handling would be a better option.
      # For now, just add a description of problem.
      mutual_connections = (
          "Automation using 'search' command could not scrape information of\n"
          '  shared connections properly.\n'
          '  Please be kind and send us a pull request :)')
      profileurl = utils.GetElementByXPath(
          _SearchResultsPageElementsPathSelectors.
          get_search_results_person_li_card_link_xpath(i +
                                                       1)).get_attribute('href')
      connect_button = utils.GetElementByXPath(
          _SearchResultsPageElementsPathSelectors.
          get_search_results_person_li_connect_button_xpath(i + 1))

      # Yield the `_Person` object after calling
      # `_Person.extract_profileid_from_profileurl()` on profile URL to get
      # profile ID.
      yield _Person(name, degree, occupation, location, mutual_connections,
                    _Person.extract_profileid_from_profileurl(profileurl),
                    profileurl, connect_button)
      person_li_count += 1

    # Stop yielding if the counter reaches the maximum invitation limit.
    if person_li_count == connect.LINKEDIN_MAX_INVITATION_LIMIT:
      return

    def goto_next_page() -> None:
      """Goes to the next page.

      Nested function used by function `_GetSearchResultsPersonLiObject()` to
      go to the next page once all the `li` elements are scraped.
      """
      next_button = driver.GetGlobalChromeDriverInstance(
      ).find_element_by_xpath(_SearchResultsPageElementsPathSelectors.
                              get_goto_next_page_button_xpath())

      # It is important to go over the button before performing click on it
      # because for some reason if we don't do this we will encounter a
      # `NoSuchElementException`.
      action_chains.ActionChains(
          driver.GetGlobalChromeDriverInstance()).move_to_element(
              next_button).click().perform()

    try:
      # Try going to the next page.
      goto_next_page()
    except exceptions.NoSuchElementException:
      # If the `NoSuchElementException` is raised that means that the button
      # to go to the next page is present but we need to scroll the page first.
      javascript.JS.load_page()
      goto_next_page()


class LinkedInSearchConnect:
  """Interface to interact with the LinkedIn's Search bar to get search
  results page.

  This interface gives functions to request the Search results page and send
  connection requests to LinkedIn users.
  """

  def __init__(self,
               *,
               keyword: str,
               location: str,
               title: str,
               firstname: str,
               lastname: str,
               school: str,
               industry: str,
               current_company: str,
               profile_language: str,
               max_connection_limit: int,
               template_file: Optional[str] = None) -> None:
    """Initializes the instance of `LinkedinInSearchConnect` class with the
    given information.

    The given `max_connection_limit` should be between 0 and 80 otherwise an
    exception is raised with the message
    `settings.CONNECTION_LIMIT_EXCEED_EXCEPTION_MESSAGE`.  If the argument
    `max_connection_limit` is `None` then the `self._max_connection_limit` is
    set to 20.

    Args:
      keyword: The keyword to search for.
      location: The location to search for.
      title: The title to search for in the person's profile.
      firstname: The first name to search for.
      lastname: The last name to search for.
      school: The school where the person can be.
      industry: The industry where the person belongs.
      current_company: The current company where the person works.
      profile_language: The language of the person's profile.
      max_connection_limit: The maximum number of connections a non-premium
                            account can send.
      template_file: The path to the message template file.
    """
    if max_connection_limit is None:
      max_connection_limit = 20
    elif not 0 < max_connection_limit <= 80:
      raise ValueError(settings.CONNECTION_LIMIT_EXCEED_EXCEPTION_MESSAGE %
                       (max_connection_limit))
    self._max_connection_limit = max_connection_limit

    if keyword is None:
      raise ValueError(
          "Function expects at least one argument 'keyword'. Provide a industry"
          " keyword such as 'Software Developer', 'Hacker' or you can pass in"
          " someone's name like 'Mohika' you want to connect with.")
    self._keyword = keyword
    self._location = location
    self._title = title
    self._firstname = firstname
    self._lastname = lastname
    self._school = school
    self._industry = industry
    self._current_company = current_company
    self._profile_language = profile_language

    if template_file is not None:
      # Read the invitation message if the template file path is given.
      self._invitation_message = template.ReadTemplate(template_file)
    else:
      self._invitation_message = None

  def get_search_results_page(self) -> None:
    """Requests the search results page by entering the given `keyword` by
    the user.
    """
    # Get the `PathSelectorBuilder` object for 'typeahead input box'.
    typeahead_input_box_psb = _SearchResultsPageElementsPathSelectors.get_global_nav_typeahead_input_box_xpath()  # pylint: disable=line-too-long
    # Get the 'typeahead input box' itself by its `xpath`.
    typeahead_input_box = self._get_element_by_xpath(
        str(typeahead_input_box_psb))
    try:
      # Try clearing it before entering any input.
      typeahead_input_box.clear()
    except exceptions.InvalidElementStateException:
      logger.error('%s Element is in invalid state at: %s for label: %s',
                   traceback.format_exc().strip('\n').strip(),
                   str(typeahead_input_box_psb),
                   typeahead_input_box_psb.path_label)
    # Send the `keyword` entered by the user in the command line.
    typeahead_input_box.send_keys(self._keyword)
    # Send `RETURN` key to start searching for results.
    typeahead_input_box.send_keys(keys.Keys.RETURN)

  def _get_element_by_xpath(self,
                            xpath: pathselectorbuilder.PathSelectorBuilder,
                            wait: int = 10) -> webdriver.Chrome:
    """Returns a single `WebElement` that is located at the given
    `PathSelectorBuilder` object.

    Args:
      xpath: `PathSelectorBuilder` object for the element to return.
      wait: Explicit timeout if we fail to locate the element.

    Returns:
      `WebElement` located at the given `PathSelectorBuilder` object.
    """
    return WebDriverWait(driver.GetGlobalChromeDriverInstance(), wait).until(
        EC.presence_of_element_located((by.By.XPATH, str(xpath))))

  def _get_elements_by_xpath(self,
                             xpath: pathselectorbuilder.PathSelectorBuilder,
                             wait: int = 10) -> list[webdriver.Chrome]:
    """Returns a list of `WebElement`s that is located at the given
    `PathSelectorBuilder` object.

    Args:
      xpath: `PathSelectorBuilder` object for the elements to return.
      wait: Explicit timeout if we fail to locate the elements.

    Returns:
      List of `WebElement`s located at the given `PathSelectorBuilder` object.
    """
    return WebDriverWait(driver.GetGlobalChromeDriverInstance(), wait).until(
        EC.presence_of_all_elements_located((by.By.XPATH, str(xpath))))

  def _check_if_any_filter_is_given(self) -> bool:
    """Returns a boolean `True` if user had given a filter along with its
    search query in the command line.

    Returns:
      Boolean `True` if any filter is given, `False` otherwise.
    """
    return any([
        self._location, self._industry, self._profile_language, self._firstname,
        self._lastname, self._title, self._current_company, self._school
    ])

  def _apply_filters_to_search_results(self):
    """Applies filters to search results if given any."""

    # This is the first most filter that must be applied to the page even
    # if user has not given any filter over the command line.
    # This filter narrows down the search results to just people and kicks
    # out other useless things like posts, pages, groups, etc.
    filter_by_people_button = self._get_element_by_xpath(
        _SearchResultsPageElementsPathSelectors.
        get_filter_by_people_button_xpath())
    filter_by_people_button.click()

    # Once the click operation has been performed we deletes the object
    # because it's going to take a lot of space in the memory so the other
    # objects in this function; we don't want stack overflow so we free-up
    # the memory that's not in use anymore.
    del filter_by_people_button

    if self._check_if_any_filter_is_given():
      # Bring out the Filters overlay if any filter is given.
      all_filters_button = self._get_element_by_xpath(
          _SearchResultsPageElementsPathSelectors.get_all_filters_button_xpath(
          ))
      all_filters_button.click()

      # Delete the `all_filters_button` to free-up memory that is not in use
      # anymore.
      del all_filters_button

    def apply_if_filter_is_valid(
        filter: Union[str, list],  # pylint: disable=redefined-builtin
        filter_dict: dict[str, webdriver.Chrome]
    ) -> None:
      """Clicks on the checkboxes that are there for filters.

      Only clicks those checkboxes that are present in the given `filter` object
      and if present in the given `filter_dict`.

      Args:
        filter: Filter given by the user over the command line.
        filter_dict: Dictionary containing all filters in the filters overlay
                     with their respective checkboxe webelement.
      """
      nonlocal self

      # Create a list of all the filters present on the overlay for a particular
      # section by dumping all the keys of the given `filter_dict`.
      filters_present: list[str] = filter_dict.keys()

      def click_overlapped_element(element: webdriver.Chrome) -> None:
        """Nested function click_overlapped_element() fixes the
        WebdriverException: Element is not clickable at point (..., ...).

        Args:
          element: Element to perform click operation on.
        """
        nonlocal self
        # @TODO: Validate if the current version of this function is efficient
        driver.GetGlobalChromeDriverInstance().execute_script(
            'arguments[0].click();', element)

      if isinstance(filter, str):
        if filter in filters_present:
          # Perform click operation once it has been confired that the user
          # given filter is present on the overlay.
          click_overlapped_element(filter_dict[filter])
        else:
          raise RuntimeError('Given filter "' + filter + '" is not present.')
        return

      if isinstance(filter, list):
        for fltr in filter:
          # Iterate over the `filter` list and check if any of the filter is
          # present on the filters overlay.
          if fltr in filters_present:
            # Perform click operation once it has been confired that the user
            # given filter is present on the overlay.
            click_overlapped_element(filter_dict[fltr])
            continue
          else:
            raise RuntimeError('Given filter "' + fltr + '" is not present.')
        return

    def apply_if_filter_is_valid_with_processed_filter_options_and_labels(
        filter: Union[str, list],  # pylint: disable=redefined-builtin
        options_psb: pathselectorbuilder.PathSelectorBuilder,
        labels_psb: pathselectorbuilder.PathSelectorBuilder,
        tag_name: str) -> None:
      """Calls function `apply_if_filter_is_valid()` with processed data.

      This function takes out the filters available for a particular section
      in the filters overlay and sends them to the function
      `apply_if_filter_is_valid()` which then checks if the user given
      filter(s) is present on the overlay and then clicks on them.

      Args:
        filter: Filter given by the user over the command line.
        options_psb: `PathSelectorBuilder` object for the options of the filter.
        labels_psb: `PathSelectorBuilder` object for the labels of the filter.
        tag_name: Tag name to search the labels in.
      """
      # Fetch the available filter options in a list.
      available_filters_options = self._get_elements_by_xpath(options_psb)
      # Fetch the available filter names in a list. Filter names are named as
      # labels in the filters overlay.
      available_filters: list[str] = [
          label.find_element_by_tag_name(tag_name).text
          for label in self._get_elements_by_xpath(labels_psb)
      ]
      filters_dict: dict[str, webdriver.Chrome] = {}
      for fltr, filter_option in zip(available_filters,
                                     available_filters_options):
        # Map each filter name with its checkbox webelement.
        filters_dict[fltr] = filter_option

      # Pass the `filter` object with the generated `filters_dict` to function
      # `apply_if_filter_is_valid()`.
      apply_if_filter_is_valid(filter, filters_dict)

    if self._location:
      apply_if_filter_is_valid_with_processed_filter_options_and_labels(
          self._location,
          _SearchResultsPageElementsPathSelectors.
          get_available_location_options_xpath(),
          _SearchResultsPageElementsPathSelectors.
          get_available_location_labels_xpath(), 'span')

    if self._industry:
      apply_if_filter_is_valid_with_processed_filter_options_and_labels(
          self._industry,
          _SearchResultsPageElementsPathSelectors.
          get_available_industry_options_xpath(),
          _SearchResultsPageElementsPathSelectors.
          get_available_industry_labels_xpath(), 'span')

    if self._profile_language:
      apply_if_filter_is_valid_with_processed_filter_options_and_labels(
          self._profile_language,
          _SearchResultsPageElementsPathSelectors.
          get_available_profile_language_options_xpath(),
          _SearchResultsPageElementsPathSelectors.
          get_available_profile_langauge_labels_xpath(), 'span')

    def apply_filter_with_its_input_value(
        filter: str,  # pylint: disable=redefined-builtin
        psb: pathselectorbuilder.PathSelectorBuilder,
        tag_name: str) -> None:
      """Sends the given `filter` value at the given `psb` location.

      Args:
        filter: Filter to enter inside the element located at given `psb`.
        psb: `PathSelectorBuilder` object of the element where we want to put
             the given `filter` in.
        tag_name: Tag name by which we will locate the element.
      """
      input_element = self._get_elements_by_xpath(
          str(psb)).find_element_by_tag_name(tag_name)
      input_element.clear()
      input_element.send_keys(filter)

    if self._firstname:
      apply_filter_with_its_input_value(
          self._firstname,
          _SearchResultsPageElementsPathSelectors.
          get_first_name_input_element_container_xpath(), 'input')

    if self._lastname:
      apply_filter_with_its_input_value(
          self._lastname,
          _SearchResultsPageElementsPathSelectors.
          get_last_name_input_element_container_xpath(), 'input')

    if self._title:
      apply_filter_with_its_input_value(
          self._title,
          _SearchResultsPageElementsPathSelectors.
          get_title_input_element_container_xpath(), 'input')

    if self._current_company:
      apply_filter_with_its_input_value(
          self._current_company,
          _SearchResultsPageElementsPathSelectors.
          get_current_company_input_element_container_xpath(), 'input')

    if self._school:
      apply_filter_with_its_input_value(
          self._school,
          _SearchResultsPageElementsPathSelectors.
          get_school_input_element_container_xpath(), 'input')

    if self._check_if_any_filter_is_given():
      # If any filter was given that means we have marked some checkboxes
      # so now we need to proceed by clicking on the 'Apply current filter'
      # button.
      apply_current_filters_button = self._get_element_by_xpath(
          _SearchResultsPageElementsPathSelectors.
          get_apply_current_filters_button_xpath())
      apply_current_filters_button.click()

      # Delete `apply_current_filters_button` to free-up memory that is not
      # in use anymore.
      del apply_current_filters_button

  def send_connection_requests(self) -> None:
    """Sends connection requests to people in search results page carried out
    by the driver program.

    Sends connection requests to people in the Search results page.  Explicitly
    waits until the elements that contains user information pops themselves up
    on the page.  This explicit wait is important that we achieve using the
    `WebDriverWait` API because LinkedIn is a dynamic website and will not pop
    the elements on the page until requested.  Protected function
    `utils.GetElementByXPath()` helps finding out the elements from the
    `document_object_module` by explicitly requesting elements from the dynamic
    page by triggering a scroll down event.

    You will also see the user's information printed on the console as this
    function sends connection request on LinkedIn.  `Invitation` API handles
    the printing of the information on the console.
    """

    # Apply all the user given (if any) filter information on the
    # 'Search results' page.
    self._apply_filters_to_search_results()

    # Set invitation count to 0 before sending any invitation request.
    invitation_count = 0
    start_time = time.time()

    invitation = status.Invitation()

    # Request the generator function to yield `_Person` objects that are
    # generated on the 'Search results' page.
    for person in _GetSearchResultsPersonLiObject():

      # If the text on the `connect_button` is 'Pending' (means we've already
      # sent invitation and it is on pending) or the aria-label of
      # `connect_button` is either of ('Follow', 'Message') than we want to
      # continue the loop as clicking on these buttons will not have a
      # desirable result.
      if (person.connect_button.text == 'Pending' or
          person.connect_button.get_attribute('aria-label')
          in ('Follow', 'Message')):
        continue
      try:
        # Move to the element on the page to avoid
        # `ElementNotInteractableException`.
        action_chains.ActionChains(
            driver.GetGlobalChromeDriverInstance()).move_to_element(
                person.connect_button).click().perform()

        # Get the 'Send now' button from the dialog that appears after clicking
        # on the `connect_button`.
        send_now_button = self._get_element_by_xpath(
            _SearchResultsPageElementsPathSelectors.get_send_invite_modal_xpath(
            )).find_element_by_xpath(_SearchResultsPageElementsPathSelectors.
                                     get_send_now_button_xpath())

        # Move to the element on the page to avoid
        # `ElementNotInteractableException`.
        action_chains.ActionChains(
            driver.GetGlobalChromeDriverInstance()).move_to_element(
                send_now_button).click().perform()
        invitation.display_invitation_status_on_console(person, 'sent',
                                                        start_time)

        # Increment the invitation count.
        invitation_count += 1
      except (exceptions.ElementNotInteractableException,
              exceptions.ElementClickInterceptedException) as exc:
        logger.error(traceback.format_exc())

        # If the element is not interactable or click intercepted then we
        # assume that the page is unable to send the invitation request and
        # there's a serious problem so we just break the loop.
        if isinstance(exc, exceptions.ElementClickInterceptedException):
          break
        invitation.display_invitation_status_on_console(person, 'failed',
                                                        start_time)

      # Check if the invitation count is equal to the maximum number of
      # connections a non-premium account can send.
      if invitation_count == self._max_connection_limit:
        break
